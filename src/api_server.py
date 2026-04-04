"""Local web API for Background Remover Studio.

Endpoints
---------
GET  /                         → Web UI (static HTML)
GET  /api/health               → Health check
GET  /api/info                 → Version, capabilities
POST /api/remove-background    → Remove background from image

Input modes (POST /api/remove-background)
------------------------------------------
1. multipart/form-data   — field "file" (UploadFile)
2. application/json      — field "image_base64" (base64-encoded image)

Response modes (response_format parameter)
-------------------------------------------
image  (default) → binary image stream (PNG/WebP/JPG)
json             → JSON object with base64-encoded result and metadata

JSON response example
----------------------
{
  "success": true,
  "image": {
    "data": "<base64>",
    "format": "png",
    "media_type": "image/png",
    "width": 1920,
    "height": 1080
  },
  "source": {
    "filename": "photo.jpg",
    "width": 1920,
    "height": 1080
  },
  "processing": {
    "white_threshold": 225,
    "edge_cleanup": 0,
    "hair_protect": true,
    "mode": "photo"
  }
}

LLM / function-calling compatibility
--------------------------------------
Use response_format=json with output=png for predictable, parseable output.
The JSON schema above is stable and versioned via X-API-Version header.
"""

from __future__ import annotations

import base64
import io
from pathlib import Path
from typing import Annotated, Optional

from fastapi import FastAPI, File, Form, HTTPException, Request, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from PIL import Image
from pydantic import BaseModel

from _paths import resource
from background_remover import (
    descontaminar_bordas,
    erosao_alpha,
    estimate_background_color,
    is_artwork_like_image,
    limpar_bordas,
    prepare_export_image,
    processing_profile,
    proteger_fios_de_cabelo,
    refinar_alpha_com_fundo,
    reforcar_detalhes_de_arte,
    sanitizar_rgb_transparente,
    suavizar_borda_humana,
    suavizar_serrilhado_alpha,
)

try:
    from rembg import new_session, remove as rembg_remove
except ImportError as exc:  # pragma: no cover
    raise RuntimeError(
        "Install dependencies from requirements.txt before running the web app."
    ) from exc


# ── Constants ─────────────────────────────────────────────────────────────────

API_VERSION = "1.1.0"
WEB_DIR = resource("webui")

_EXPORT_MAP = {
    "png":  ("PNG",  "image/png",   True,  ".png"),
    "webp": ("WEBP", "image/webp",  True,  ".webp"),
    "jpg":  ("JPEG", "image/jpeg",  False, ".jpg"),
}

_SESSION = None


# ── Session ───────────────────────────────────────────────────────────────────

def get_session():
    global _SESSION
    if _SESSION is None:
        _SESSION = new_session()
    return _SESSION


# ── Core pipeline (shared with desktop app) ───────────────────────────────────

def run_pipeline(
    src: Image.Image,
    white_threshold: int = 225,
    edge_cleanup: int = 0,
    hair_protect: bool = True,
) -> tuple[Image.Image, str]:
    """Remove background from an RGB image.

    Returns (result_image, mode) where mode is 'artwork' or 'photo'.
    """
    src = src.convert("RGB")
    buffer = io.BytesIO()
    src.save(buffer, format="PNG")
    data = buffer.getvalue()

    bg_rgb = estimate_background_color(src)
    bg_brightness = float(bg_rgb.mean())
    artwork_mode = is_artwork_like_image(src, bg_rgb)
    erode_size, clean_threshold, edge_radius = processing_profile(
        src.width, src.height, white_threshold
    )

    try:
        if not artwork_mode:
            out = rembg_remove(
                data,
                session=get_session(),
                alpha_matting=True,
                alpha_matting_foreground_threshold=240,
                alpha_matting_background_threshold=10,
                alpha_matting_erode_size=erode_size,
            )
        else:
            out = rembg_remove(data, session=get_session())
    except Exception:
        out = rembg_remove(data, session=get_session())

    img = Image.open(io.BytesIO(out)).convert("RGBA")

    if artwork_mode:
        img = reforcar_detalhes_de_arte(src, img, bg_rgb, distance_threshold=26.0)
        img = sanitizar_rgb_transparente(img)
    else:
        img = refinar_alpha_com_fundo(
            src, img, bg_rgb,
            edge_radius=max(3, edge_radius + 1),
            low=18.0, high=92.0,
        )
        if hair_protect:
            img = proteger_fios_de_cabelo(src, img, bg_rgb, edge_radius=max(2, edge_radius))
        sim_thr = 46.0 if bg_brightness < 170.0 else 62.0
        img = descontaminar_bordas(
            img, bg_rgb,
            edge_radius=max(2, edge_radius),
            similarity_threshold=sim_thr,
        )
        if clean_threshold < 255:
            cleanup_thr = clean_threshold if bg_brightness < 170.0 else min(clean_threshold, 212)
            img = limpar_bordas(img, cleanup_thr, edge_radius=edge_radius)
        img = suavizar_borda_humana(src, img, bg_rgb, edge_radius=max(1, edge_radius))
        img = suavizar_serrilhado_alpha(img, edge_radius=max(1, edge_radius), blur_radius=0.72)
        if edge_cleanup > 0:
            img = erosao_alpha(img, edge_cleanup)
        img = sanitizar_rgb_transparente(img)

    mode = "artwork" if artwork_mode else "photo"
    return img, mode


def _encode_image(img: Image.Image, fmt: str) -> tuple[bytes, str, str]:
    """Encode a PIL image to bytes.

    Returns (image_bytes, pil_format, media_type).
    """
    fmt = fmt if fmt in _EXPORT_MAP else "png"
    pil_format, media_type, transparent, _ = _EXPORT_MAP[fmt]
    final = prepare_export_image(img, transparent)
    buf = io.BytesIO()
    save_kwargs = {"quality": 95} if pil_format in {"WEBP", "JPEG"} else {}
    final.save(buf, format=pil_format, **save_kwargs)
    return buf.getvalue(), pil_format, media_type, final.width, final.height


def _load_image_from_bytes(raw: bytes) -> Image.Image:
    """Load and validate a PIL image from raw bytes."""
    try:
        return Image.open(io.BytesIO(raw)).convert("RGB")
    except Exception as exc:
        raise HTTPException(status_code=400, detail="Invalid or unreadable image file.") from exc


# ── FastAPI app ───────────────────────────────────────────────────────────────

app = FastAPI(
    title="Background Remover Studio API",
    description=(
        "Local-first background removal API. "
        "Accepts file upload or base64-encoded images. "
        "Returns image binary (default) or JSON with base64 result."
    ),
    version=API_VERSION,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# CORS — allow any origin for local / LLM tool use
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=[
        "X-API-Version",
        "X-Image-Width",
        "X-Image-Height",
        "X-Processing-Mode",
        "Content-Disposition",
    ],
)

app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")


# ── Standard response headers ─────────────────────────────────────────────────

def _base_headers(width: int, height: int, mode: str) -> dict[str, str]:
    return {
        "X-API-Version": API_VERSION,
        "X-Image-Width": str(width),
        "X-Image-Height": str(height),
        "X-Processing-Mode": mode,
    }


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    return FileResponse(WEB_DIR / "index.html")


@app.get(
    "/api/health",
    summary="Health check",
    tags=["Meta"],
)
def health():
    """Returns 200 OK when the API is running."""
    return JSONResponse(
        {"ok": True, "app": "Background Remover Studio API", "version": API_VERSION},
        headers={"X-API-Version": API_VERSION},
    )


@app.get(
    "/api/info",
    summary="API capabilities and schema info",
    tags=["Meta"],
)
def info():
    """Describes the API capabilities — useful for LLM tool discovery."""
    return JSONResponse({
        "name": "Background Remover Studio API",
        "version": API_VERSION,
        "description": "Remove backgrounds from images locally. No cloud, no limits.",
        "endpoints": {
            "remove_background": {
                "method": "POST",
                "path": "/api/remove-background",
                "input_modes": ["multipart/form-data (file)", "application/json (base64)"],
                "response_modes": ["image (binary stream)", "json (base64 + metadata)"],
                "supported_formats": list(_EXPORT_MAP.keys()),
            }
        },
        "docs": "/api/docs",
    })


# ── Pydantic model for JSON input ─────────────────────────────────────────────

class RemoveBackgroundJSON(BaseModel):
    """JSON body for base64 image input."""
    image_base64: str
    """Base64-encoded image (with or without data URI prefix)."""

    filename: str = "image.png"
    """Original filename — used only to name the output file."""

    white_threshold: int = 225
    """White/light background sensitivity (180–255). Default 225."""

    edge_cleanup: int = 0
    """Edge erosion strength (0–8). Default 0."""

    hair_protect: bool = True
    """Preserve fine hair/fur details. Default true."""

    output: str = "png"
    """Output format: png, webp, jpg. Default png."""

    response_format: str = "json"
    """Response format: image (binary) or json (base64). Default json."""


# ── Main endpoint ─────────────────────────────────────────────────────────────

@app.post(
    "/api/remove-background",
    summary="Remove background from an image",
    tags=["Processing"],
    responses={
        200: {
            "description": (
                "Processed image. Returns binary stream when response_format=image, "
                "or JSON object when response_format=json."
            )
        },
        400: {"description": "Invalid input (bad image, missing file, etc.)"},
        422: {"description": "Validation error (bad parameter values)"},
    },
)
async def remove_background(
    request: Request,
    # ── multipart/form-data fields ──
    file: Optional[UploadFile] = File(None),
    white_threshold: Annotated[int, Form(ge=180, le=255)] = Form(225),
    edge_cleanup: Annotated[int, Form(ge=0, le=8)] = Form(0),
    hair_protect: bool = Form(True),
    output: str = Form("png"),
    response_format: str = Form("image"),
):
    """Remove the background from an uploaded image.

    **Input**

    Send as `multipart/form-data` with a `file` field, or send
    `application/json` with an `image_base64` field (base64-encoded image,
    optionally with a data URI prefix).

    **Output**

    - `response_format=image` (default for form upload): binary image stream
    - `response_format=json` (default for JSON input): JSON object with
      base64-encoded result image and processing metadata

    **LLM / function-calling usage**

    POST `application/json` with `image_base64` and `response_format=json`
    for a structured, parseable response.
    """
    content_type = request.headers.get("content-type", "")

    # ── Branch: JSON body with base64 ─────────────────────────────────────────
    if "application/json" in content_type:
        try:
            body = await request.json()
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid JSON body.") from exc

        image_b64: str = body.get("image_base64", "")
        if not image_b64:
            raise HTTPException(status_code=400, detail="Field 'image_base64' is required.")

        # Strip optional data URI prefix (data:image/png;base64,...)
        if "," in image_b64:
            image_b64 = image_b64.split(",", 1)[1]

        try:
            raw = base64.b64decode(image_b64)
        except Exception as exc:
            raise HTTPException(status_code=400, detail="Invalid base64 encoding.") from exc

        filename      = str(body.get("filename", "image.png"))
        white_threshold = max(180, min(255, int(body.get("white_threshold", 225))))
        edge_cleanup  = max(0, min(8, int(body.get("edge_cleanup", 0))))
        hair_protect  = bool(body.get("hair_protect", True))
        output        = str(body.get("output", "png"))
        response_format = str(body.get("response_format", "json"))  # default json for API callers

    # ── Branch: multipart/form-data ───────────────────────────────────────────
    else:
        if file is None or not file.filename:
            raise HTTPException(status_code=400, detail="No file uploaded. Send a file via 'file' field.")
        raw = await file.read()
        filename = file.filename
        # clamp values (already validated by Form annotations above)
        white_threshold = max(180, min(255, white_threshold))
        edge_cleanup    = max(0, min(8, edge_cleanup))

    # ── Load image ────────────────────────────────────────────────────────────
    src_img = _load_image_from_bytes(raw)
    src_width, src_height = src_img.width, src_img.height

    # ── Run pipeline ──────────────────────────────────────────────────────────
    result_img, proc_mode = run_pipeline(
        src_img,
        white_threshold=white_threshold,
        edge_cleanup=edge_cleanup,
        hair_protect=hair_protect,
    )

    # ── Encode output ─────────────────────────────────────────────────────────
    fmt = output if output in _EXPORT_MAP else "png"
    image_bytes, pil_format, media_type, out_w, out_h = _encode_image(result_img, fmt)
    _, _, _, suffix = _EXPORT_MAP[fmt][:4]  # not used below but kept for reference
    suffix = _EXPORT_MAP[fmt][3]
    stem   = Path(filename).stem or "result"

    base_hdrs = _base_headers(out_w, out_h, proc_mode)

    # ── Return JSON ───────────────────────────────────────────────────────────
    if response_format == "json":
        return JSONResponse(
            content={
                "success": True,
                "image": {
                    "data": base64.b64encode(image_bytes).decode(),
                    "format": fmt,
                    "media_type": media_type,
                    "width": out_w,
                    "height": out_h,
                },
                "source": {
                    "filename": filename,
                    "width": src_width,
                    "height": src_height,
                },
                "processing": {
                    "white_threshold": white_threshold,
                    "edge_cleanup": edge_cleanup,
                    "hair_protect": hair_protect,
                    "mode": proc_mode,
                },
            },
            headers=base_hdrs,
        )

    # ── Return binary stream ──────────────────────────────────────────────────
    headers = {
        **base_hdrs,
        "Content-Disposition": f'inline; filename="{stem}_transparent{suffix}"',
    }
    return StreamingResponse(io.BytesIO(image_bytes), media_type=media_type, headers=headers)
