# Developed by Henrique Fernandes
# Instagram / company: @oportunipt
# LinkedIn: https://pt.linkedin.com/in/henriquehsf

"""
Removedor de Fundo de Imagens
"""
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading, os, io, sys
from pathlib import Path
import ctypes

try:
    from PIL import Image, ImageTk, ImageFilter, ImageDraw
    import numpy as np
except ImportError:
    root = tk.Tk(); root.withdraw()
    messagebox.showerror("Startup Error", "Please launch the app with start.bat.")
    sys.exit(1)

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    TK_ROOT = TkinterDnD.Tk
    DND_READY = True
except ImportError:
    DND_FILES = None
    TK_ROOT = tk.Tk
    DND_READY = False

rembg_remove = None
rembg_pronto = False
rembg_new_session = None

# ── Cores ────────────────────────────────────────────────────
BG          = "#0B0F14"
TOP_BG      = "#0E131A"
CARD        = "#111827"
CARD2       = "#161D28"
BORDER      = "#222B38"
BORDER_SOFT = "#2A3442"
ACCENT      = "#3994FF"
ACCENT_ALT  = "#67AEFF"
ACCENT_GOLD = "#E8BC72"
ACCENT_CYAN = "#8FD3FF"
SUCCESS     = "#3DD68C"
ERROR       = "#FF7F7F"
TEXT        = "#F7F9FC"
DIM         = "#9CA7B5"
MUTED       = "#6E7888"
SOFT_TEXT   = "#DCE4EE"
PREVIEW_BG  = "#0A1017"
EXTS    = {".png",".jpg",".jpeg",".webp",".bmp",".tiff",".tif"}

EXPORT_FORMATS = {
    "png":  {"ext": ".png",  "pil_format": "PNG",  "transparent": True},
    "webp": {"ext": ".webp", "pil_format": "WEBP", "transparent": True},
    "tiff": {"ext": ".tiff", "pil_format": "TIFF", "transparent": True},
    "jpg":  {"ext": ".jpg",  "pil_format": "JPEG", "transparent": False},
    "bmp":  {"ext": ".bmp",  "pil_format": "BMP",  "transparent": False},
}

I18N = {
    "en": {
        "app_title": "Background Remover Studio",
        "header_title": "Remove Background",
        "header_subtitle": "High quality transparent PNG",
        "lang_en": "EN",
        "lang_pt": "PTBR",
        "simple_mode": "Simple Mode",
        "simple_mode_sub": "Minimal workflow for quick cutouts",
        "your_images": "Your Images",
        "your_images_sub": "Select an image to preview and export.",
        "add": "Add",
        "folder": "Folder",
        "remove": "Remove",
        "export": "Export",
        "same_folder": "Same folder as source image",
        "change_folder": "Change Folder",
        "export_png": "Export PNG",
        "export_file": "Export File",
        "copy_image": "Copy Image",
        "format_png": "PNG transparent",
        "format_webp": "WebP transparent",
        "format_tiff": "TIFF transparent",
        "format_jpg": "JPG white background",
        "format_bmp": "BMP white background",
        "process_selected_only": "Process selected image only",
        "manual_tools": "Manual Cleanup",
        "manual_tools_sub": "Paint to restore hair/details or cut away leftover background.",
        "manual_tools_sub_short": "Restore strands/details or snip leftover background.",
        "manual_tool": "Tool",
        "tool_none": "Off",
        "tool_restore": "Restore Area",
        "tool_cut": "Cut / Remove",
        "tool_move": "Move Preview",
        "brush_size": "Brush Size",
        "brush_shape": "Brush Shape",
        "shape_round": "Round",
        "shape_square": "Square",
        "shape_triangle": "Triangle",
        "shape_pencil": "Pencil",
        "manual_tip": "Paint on the right preview. Hold Shift or use Move to pan while zoomed.",
        "hair_protect": "Hair Protect",
        "hair_protect_sub": "Preserve fine strands and trim loose background near hair.",
        "sticker_mode": "Sticker Mode",
        "sticker_mode_sub": "Flood-fill removes only the outer background. Keeps white areas inside the design intact.",
        "bg_colors_title": "Background Colors",
        "bg_colors_sub": "Auto-detected colors to remove. Click a swatch to keep that color.",
        "color_tolerance": "Tolerance",
        "spill_suppress": "Decontaminate Edges",
        "reapply_colors": "Re-apply Color Filter",
        "color_filter_done": "Color filter re-applied.",
        "export_resized_original": "Export Resized Original",
        "export_resized_original_sub": "Saves the original image at the chosen dimensions, without removing the background.",
        "toggle_adjustments_hide": "Hide Adjustments",
        "toggle_adjustments_show": "Show Adjustments",
        "quick_tools": "Quick Tools",
        "quick_tools_open": "Tools",
        "quick_tools_close": "Close",
        "undo": "Undo",
        "redo": "Redo",
        "undo_done": "Last manual cleanup stroke undone.",
        "redo_done": "Manual cleanup stroke restored.",
        "undo_empty": "Nothing left to undo.",
        "redo_empty": "Nothing left to redo.",
        "output_size": "Output Size",
        "output_size_sub": "Resize the final export only when needed.",
        "resize_enable": "Resize on export",
        "width_label": "Width",
        "height_label": "Height",
        "lock_ratio": "Lock ratio",
        "original_size": "Original: {width} x {height}px",
        "original_select": "Original: select an image",
        "preview": "Preview",
        "preview_sub": "Compare original and processed output",
        "before": "Before",
        "after": "After",
        "split": "Split",
        "fit": "Fit",
        "adjustments": "Adjustments",
        "adjustments_sub": "Fine-tune cleanup and export the final PNG.",
        "white_threshold": "White Threshold",
        "edge_cleanup": "Edge Cleanup",
        "remove_bg": "Remove Background",
        "refine_edges": "Refine Edges",
        "simple_note": "Simple Mode keeps the workflow minimal. Turn it off for manual tuning.",
        "original": "ORIGINAL",
        "removed": "REMOVED",
        "no_image": "No image selected",
        "not_processed": "Not processed yet",
        "no_images_yet": "No images yet.\nAdd one to get started.",
        "ready": "Ready",
        "processed": "Processed",
        "refined": "Refined",
        "needs_attention": "Needs attention",
        "loading_model": "Loading model...",
        "unavailable": "Unavailable",
        "removing_short": "Removing...",
        "processing": "Processing",
        "loading_remove_sub": "Applying background removal",
        "loading_refine_sub": "Refining edges",
        "loading_reprocess_sub": "Reprocessing image",
        "ready_status": "Ready. Add an image and start removing the background.",
        "queue_status": "{count} image(s) ready in the queue.",
        "done_status": "Done. {ok}/{total} image(s) processed.",
        "processing_status": "Processing ({current}/{total}): {name}",
        "refining_status": "Refining edges...",
        "refining_done": "Edge refinement applied.",
        "reprocess_status": "Reprocessing image...",
        "reprocess_done": "Image reprocessed.",
        "startup_error": "Startup error: please open the app using start.bat.",
        "no_images_title": "No images",
        "no_images_msg": "Add at least one image first.",
        "no_pending_title": "Nothing to process",
        "no_pending_msg": "All queued images already have a processed result.",
        "reprocess_selected_status": "Reprocessing the selected image with the current settings.",
        "nothing_selected_title": "Nothing selected",
        "nothing_selected_msg": "Select an image first.",
        "process_first_title": "Process first",
        "process_first_msg": "Run background removal before refining edges.",
        "refine_first_title": "Refine first",
        "refine_first_msg": "Apply edge refinement before exporting.",
        "select_images": "Select images",
        "images_filetype": "Images",
        "all_files": "All files",
        "select_folder": "Select folder",
        "choose_export_folder": "Choose export folder",
        "exported_status": "Exported {name}  |  {size}  |  {folder}",
        "refined_exported_status": "Refined version exported to {folder}.",
        "copied_status": "Copied processed image to the clipboard.",
        "clipboard_error_title": "Clipboard error",
        "clipboard_error_msg": "Unable to copy the image to the clipboard.",
        "drop_status": "Images added via drag and drop.",
        "drop_not_available": "Drag and drop is unavailable. Install dependencies with start.bat.",
    },
    "pt": {
        "app_title": "Studio Removedor de Fundo",
        "header_title": "Remover Fundo",
        "header_subtitle": "PNG transparente em alta qualidade",
        "lang_en": "EN",
        "lang_pt": "PTBR",
        "simple_mode": "Modo Simples",
        "simple_mode_sub": "Fluxo mínimo para recortes rápidos",
        "your_images": "Suas Imagens",
        "your_images_sub": "Selecione uma imagem para visualizar e exportar.",
        "add": "Adicionar",
        "folder": "Pasta",
        "remove": "Remover",
        "export": "Exportar",
        "same_folder": "Mesma pasta da imagem de origem",
        "change_folder": "Trocar Pasta",
        "export_png": "Exportar PNG",
        "export_file": "Exportar Arquivo",
        "copy_image": "Copiar Imagem",
        "format_png": "PNG transparente",
        "format_webp": "WebP transparente",
        "format_tiff": "TIFF transparente",
        "format_jpg": "JPG com fundo branco",
        "format_bmp": "BMP com fundo branco",
        "process_selected_only": "Processar apenas a imagem selecionada",
        "manual_tools": "Limpeza Manual",
        "manual_tools_sub": "Pinte para recuperar cabelo/detalhes ou cortar restos do fundo.",
        "manual_tools_sub_short": "Recupere fios/detalhes ou corte sobras do fundo.",
        "manual_tool": "Ferramenta",
        "tool_none": "Desligado",
        "tool_restore": "Recuperar Área",
        "tool_cut": "Cortar / Remover",
        "tool_move": "Mover Preview",
        "brush_size": "Tamanho do Pincel",
        "brush_shape": "Formato do Pincel",
        "shape_round": "Redondo",
        "shape_square": "Quadrado",
        "shape_triangle": "Triangular",
        "shape_pencil": "Lápis",
        "manual_tip": "Pinte no preview da direita. Segure Shift ou use Mover para navegar com zoom.",
        "hair_protect": "Proteger Cabelo",
        "hair_protect_sub": "Preserva fios finos e corta restos soltos perto do cabelo.",
        "sticker_mode": "Modo Sticker",
        "sticker_mode_sub": "Flood fill remove apenas o fundo externo. Preserva áreas brancas internas do design.",
        "bg_colors_title": "Cores do Fundo",
        "bg_colors_sub": "Cores detectadas automaticamente. Clique numa amostra para manter aquela cor.",
        "color_tolerance": "Tolerância",
        "spill_suppress": "Descontaminar Bordas",
        "reapply_colors": "Reaplicar Filtro de Cores",
        "color_filter_done": "Filtro de cores reaplicado.",
        "export_resized_original": "Exportar Original Redimensionado",
        "export_resized_original_sub": "Salva a imagem original nas dimensões escolhidas, sem remover o fundo.",
        "toggle_adjustments_hide": "Ocultar Ajustes",
        "toggle_adjustments_show": "Mostrar Ajustes",
        "quick_tools": "Ferramentas Rápidas",
        "quick_tools_open": "Ferr.",
        "quick_tools_close": "Fechar",
        "undo": "Desfazer",
        "redo": "Refazer",
        "undo_done": "Último traço da limpeza manual desfeito.",
        "redo_done": "Traço da limpeza manual restaurado.",
        "undo_empty": "Nada para desfazer.",
        "redo_empty": "Nada para refazer.",
        "output_size": "Tamanho de Saída",
        "output_size_sub": "Redimensione apenas a exportação final quando precisar.",
        "resize_enable": "Redimensionar ao exportar",
        "width_label": "Largura",
        "height_label": "Altura",
        "lock_ratio": "Bloquear proporção",
        "original_size": "Original: {width} x {height}px",
        "original_select": "Original: selecione uma imagem",
        "preview": "Pré-visualização",
        "preview_sub": "Compare o original com o resultado processado",
        "before": "Antes",
        "after": "Depois",
        "split": "Dividido",
        "fit": "Ajustar",
        "adjustments": "Ajustes",
        "adjustments_sub": "Ajuste a limpeza e exporte o PNG final.",
        "white_threshold": "Limiar de Branco",
        "edge_cleanup": "Limpeza de Borda",
        "remove_bg": "Remover Fundo",
        "refine_edges": "Refinar Bordas",
        "simple_note": "O modo simples mantém o fluxo mínimo. Desative para ajustes manuais.",
        "original": "ORIGINAL",
        "removed": "SEM FUNDO",
        "no_image": "Nenhuma imagem selecionada",
        "not_processed": "Ainda não processado",
        "no_images_yet": "Nenhuma imagem ainda.\nAdicione uma para começar.",
        "ready": "Pronta",
        "processed": "Processada",
        "refined": "Refinada",
        "needs_attention": "Verificar",
        "loading_model": "Carregando modelo...",
        "unavailable": "Indisponível",
        "removing_short": "Removendo...",
        "processing": "Processando",
        "loading_remove_sub": "Aplicando remocao de fundo",
        "loading_refine_sub": "Refinando bordas",
        "loading_reprocess_sub": "Reprocessando imagem",
        "ready_status": "Pronto. Adicione uma imagem e remova o fundo.",
        "queue_status": "{count} imagem(ns) prontas na fila.",
        "done_status": "Concluído. {ok}/{total} imagem(ns) processada(s).",
        "processing_status": "Processando ({current}/{total}): {name}",
        "refining_status": "Refinando bordas...",
        "refining_done": "Refino de bordas aplicado.",
        "reprocess_status": "Reprocessando imagem...",
        "reprocess_done": "Imagem reprocessada.",
        "startup_error": "Erro de inicialização: abra o app usando start.bat.",
        "no_images_title": "Sem imagens",
        "no_images_msg": "Adicione pelo menos uma imagem primeiro.",
        "no_pending_title": "Nada para processar",
        "no_pending_msg": "Todas as imagens da fila já têm um resultado processado.",
        "reprocess_selected_status": "Reprocessando a imagem selecionada com as definições atuais.",
        "nothing_selected_title": "Nada selecionado",
        "nothing_selected_msg": "Selecione uma imagem primeiro.",
        "process_first_title": "Processe primeiro",
        "process_first_msg": "Execute a remocao de fundo antes de refinar.",
        "refine_first_title": "Refine primeiro",
        "refine_first_msg": "Aplique o refinamento antes de exportar.",
        "select_images": "Selecionar imagens",
        "images_filetype": "Imagens",
        "all_files": "Todos os ficheiros",
        "select_folder": "Selecionar pasta",
        "choose_export_folder": "Escolher pasta de exportação",
        "exported_status": "Exportado {name}  |  {size}  |  {folder}",
        "refined_exported_status": "Versão refinada exportada para {folder}.",
        "copied_status": "Imagem processada copiada para a área de transferência.",
        "clipboard_error_title": "Erro de área de transferência",
        "clipboard_error_msg": "Não foi possível copiar a imagem para a área de transferência.",
        "drop_status": "Imagens adicionadas por arrastar e largar.",
        "drop_not_available": "Arrastar e largar indisponível. Instale as dependências com o start.bat.",
    }
}

def fmt_size(n):
    for u in ("B","KB","MB","GB"):
        if n < 1024: return f"{n:.1f} {u}"
        n /= 1024
    return f"{n:.1f} TB"

# ── Processamento de imagem ──────────────────────────────────
def calc_resize_size(width: int, height: int,
                     target_width: int | None,
                     target_height: int | None):
    nw = target_width if target_width and target_width > 0 else width
    nh = target_height if target_height and target_height > 0 else height
    return max(1, int(nw)), max(1, int(nh))

def resize_to_dimensions(img: Image.Image,
                         target_width: int | None,
                         target_height: int | None) -> Image.Image:
    nw, nh = calc_resize_size(img.width, img.height, target_width, target_height)
    if (nw, nh) == img.size:
        return img
    if "A" in img.getbands():
        return resize_rgba_alpha_safe(img, (nw, nh))
    return img.resize((nw, nh), Image.LANCZOS)

def sanitizar_rgb_transparente(img: Image.Image, alpha_cutoff=1) -> Image.Image:
    arr = np.array(img.convert("RGBA"), dtype=np.uint8)
    alpha = arr[..., 3]
    arr[alpha <= alpha_cutoff, :3] = 0
    return Image.fromarray(arr, "RGBA")

def resize_rgba_alpha_safe(img: Image.Image, size: tuple[int, int]) -> Image.Image:
    # Evita que cores "invisiveis" de pixels transparentes vazem ao reduzir a imagem.
    src = sanitizar_rgb_transparente(img)
    arr = np.array(src, dtype=np.float32)
    alpha = arr[..., 3:4] / 255.0
    premult = arr[..., :3] * alpha
    packed = np.concatenate([premult, arr[..., 3:4]], axis=2)

    resized = Image.fromarray(np.clip(packed, 0, 255).astype(np.uint8), "RGBA")
    resized = resized.resize(size, Image.LANCZOS)

    out = np.array(resized, dtype=np.float32)
    out_alpha = out[..., 3:4] / 255.0
    safe_alpha = np.where(out_alpha > 1e-3, out_alpha, 1.0)
    rgb = np.where(out_alpha > 1e-3, out[..., :3] / safe_alpha, 0.0)
    merged = np.concatenate([np.clip(rgb, 0, 255), out[..., 3:4]], axis=2)
    return sanitizar_rgb_transparente(
        Image.fromarray(np.clip(merged, 0, 255).astype(np.uint8), "RGBA")
    )

def make_checkerboard(size: tuple[int, int], sq=12) -> Image.Image:
    w, h = size
    if w <= 0 or h <= 0:
        return Image.new("RGBA", (1, 1), (30, 30, 30, 255))
    yy, xx = np.indices((h, w))
    pattern = ((xx // sq) + (yy // sq)) % 2
    dark = np.array([18, 22, 28, 255], dtype=np.uint8)
    light = np.array([29, 34, 42, 255], dtype=np.uint8)
    arr = np.where(pattern[..., None] == 0, dark, light)
    return Image.fromarray(arr.astype(np.uint8), "RGBA")

def copy_image_to_clipboard(img: Image.Image):
    if os.name != "nt":
        raise OSError("Clipboard image copy is only supported on Windows.")

    dib_image = sanitizar_rgb_transparente(img.convert("RGBA"))
    output = io.BytesIO()
    dib_image.save(output, "BMP")
    data = output.getvalue()[14:]

    CF_DIB = 8
    GMEM_MOVEABLE = 0x0002
    user32 = ctypes.windll.user32
    kernel32 = ctypes.windll.kernel32

    hglobal = kernel32.GlobalAlloc(GMEM_MOVEABLE, len(data))
    if not hglobal:
        raise OSError("GlobalAlloc failed.")

    locked = kernel32.GlobalLock(hglobal)
    if not locked:
        kernel32.GlobalFree(hglobal)
        raise OSError("GlobalLock failed.")

    ctypes.memmove(locked, data, len(data))
    kernel32.GlobalUnlock(hglobal)

    clipboard_open = False
    try:
        if not user32.OpenClipboard(None):
            kernel32.GlobalFree(hglobal)
            raise OSError("OpenClipboard failed.")
        clipboard_open = True
        user32.EmptyClipboard()
        if not user32.SetClipboardData(CF_DIB, hglobal):
            kernel32.GlobalFree(hglobal)
            raise OSError("SetClipboardData failed.")
        hglobal = None
    finally:
        if clipboard_open:
            user32.CloseClipboard()

def prepare_export_image(img: Image.Image, transparent: bool) -> Image.Image:
    src = sanitizar_rgb_transparente(img.convert("RGBA"))
    if transparent:
        return src

    bg = Image.new("RGBA", src.size, (255, 255, 255, 255))
    bg.alpha_composite(src)
    return bg.convert("RGB")

def render_preview_image(pil_img: Image.Image, w: int, h: int, zoom=1.0) -> Image.Image:
    c = sanitizar_rgb_transparente(pil_img.copy())
    max_w = max(w - 8, 40)
    max_h = max(h - 8, 40)
    fit_scale = min(max_w / max(c.width, 1), max_h / max(c.height, 1))
    fit_scale = max(fit_scale, 0.01)
    scale = max(fit_scale * max(zoom, 0.1), 0.01)
    nw = max(1, round(c.width * scale))
    nh = max(1, round(c.height * scale))
    if "A" in c.getbands():
        return resize_rgba_alpha_safe(c, (nw, nh))
    return c.resize((nw, nh), Image.LANCZOS)

def _mask_borda_alpha(alpha: np.ndarray, edge_radius=2, alpha_cutoff=245) -> np.ndarray:
    alpha = alpha.astype(np.uint8, copy=False)
    if edge_radius <= 0:
        return alpha < 255

    pad = edge_radius
    padded = np.pad(alpha, pad_width=pad, mode="edge")
    h, w = alpha.shape
    near_edge = np.zeros((h, w), dtype=bool)

    for dy in range(-pad, pad + 1):
        for dx in range(-pad, pad + 1):
            if dx == 0 and dy == 0:
                continue
            ys = dy + pad
            xs = dx + pad
            near_edge |= padded[ys:ys + h, xs:xs + w] < alpha_cutoff

    return near_edge | (alpha < 255)

def _neighbor_sum(mask: np.ndarray, radius=1) -> np.ndarray:
    mask = mask.astype(np.uint8, copy=False)
    if radius <= 0:
        return mask.astype(np.uint16)

    pad = radius
    padded = np.pad(mask, pad_width=pad, mode="constant")
    h, w = mask.shape
    total = np.zeros((h, w), dtype=np.uint16)

    for dy in range(-pad, pad + 1):
        for dx in range(-pad, pad + 1):
            ys = dy + pad
            xs = dx + pad
            total += padded[ys:ys + h, xs:xs + w]

    return total

def estimate_background_color(img: Image.Image, sample_size=48) -> np.ndarray:
    arr = np.array(img.convert("RGB"), dtype=np.float32)
    h, w = arr.shape[:2]
    s = max(8, min(sample_size, h // 4 if h >= 4 else h, w // 4 if w >= 4 else w))
    if s <= 0:
        return np.array([255.0, 255.0, 255.0], dtype=np.float32)

    top = arr[:s, :, :].reshape(-1, 3)
    left = arr[s:h-s, :s, :].reshape(-1, 3) if h > s * 2 else top
    right = arr[s:h-s, w-s:, :].reshape(-1, 3) if h > s * 2 else top
    bottom = arr[h-s:, s:w-s, :].reshape(-1, 3) if h > s and w > s * 2 else top

    border_samples = np.concatenate([top, left, right, bottom], axis=0)
    top_ref = np.median(top, axis=0).astype(np.float32)
    top_brightness = float(np.mean(top_ref))

    border_brightness = np.mean(border_samples, axis=1)
    border_dist = np.sqrt(np.sum((border_samples - top_ref) ** 2, axis=1))

    brightness_window = np.clip(22.0 + abs(top_brightness - 128.0) * 0.18, 22.0, 52.0)
    selected = border_samples[
        (np.abs(border_brightness - top_brightness) <= brightness_window) |
        (border_dist <= 52.0)
    ]

    if selected.shape[0] < max(256, border_samples.shape[0] // 12):
        selected = top

    return np.median(selected, axis=0).astype(np.float32)

def border_distance_stats(img: Image.Image, bg_rgb: np.ndarray, sample_size=48) -> tuple[float, float]:
    arr = np.array(img.convert("RGB"), dtype=np.float32)
    h, w = arr.shape[:2]
    s = max(8, min(sample_size, h // 4 if h >= 4 else h, w // 4 if w >= 4 else w))
    if s <= 0:
        return 0.0, 0.0

    top = arr[:s, :, :].reshape(-1, 3)
    left = arr[s:h-s, :s, :].reshape(-1, 3) if h > s * 2 else top
    right = arr[s:h-s, w-s:, :].reshape(-1, 3) if h > s * 2 else top
    bottom = arr[h-s:, s:w-s, :].reshape(-1, 3) if h > s and w > s * 2 else top
    border_samples = np.concatenate([top, left, right, bottom], axis=0)
    dist = np.sqrt(np.sum((border_samples - bg_rgb.reshape(1, 3)) ** 2, axis=1))
    return float(np.mean(dist)), float(np.percentile(dist, 90))

def estimate_palette_complexity(img: Image.Image, thumb_size=160, colors=32) -> int:
    sample = img.convert("RGB").copy()
    sample.thumbnail((thumb_size, thumb_size))
    quant = sample.quantize(colors=colors, method=Image.MEDIANCUT)
    found = quant.getcolors(maxcolors=colors * 2)
    return len(found) if found else colors * 2

def estimate_background_coverage(img: Image.Image, bg_rgb: np.ndarray,
                                 thumb_size=180, threshold=18.0) -> float:
    sample = img.convert("RGB").copy()
    sample.thumbnail((thumb_size, thumb_size))
    arr = np.array(sample, dtype=np.float32)
    dist_bg = np.sqrt(np.sum((arr - bg_rgb.reshape(1, 1, 3)) ** 2, axis=2))
    return float(np.mean(dist_bg <= threshold))

def is_artwork_like_image(img: Image.Image, bg_rgb: np.ndarray) -> bool:
    bg_brightness = float(np.mean(bg_rgb))
    border_mean, border_p90 = border_distance_stats(img, bg_rgb)
    palette_bins = estimate_palette_complexity(img)
    bg_coverage = estimate_background_coverage(img, bg_rgb)
    return (
        bg_brightness >= 215.0 and
        border_mean <= 12.0 and
        border_p90 <= 26.0 and
        (bg_coverage >= 0.42 or palette_bins <= 30)
    )

def estimate_edge_strength(gray: np.ndarray) -> np.ndarray:
    padded = np.pad(gray.astype(np.float32), 1, mode="edge")
    center = padded[1:-1, 1:-1]
    diffs = [
        np.abs(center - padded[:-2, 1:-1]),
        np.abs(center - padded[2:, 1:-1]),
        np.abs(center - padded[1:-1, :-2]),
        np.abs(center - padded[1:-1, 2:]),
        np.abs(center - padded[:-2, :-2]),
        np.abs(center - padded[:-2, 2:]),
        np.abs(center - padded[2:, :-2]),
        np.abs(center - padded[2:, 2:]),
    ]
    return np.maximum.reduce(diffs)

def build_artwork_protection_alpha(original_img: Image.Image, bg_rgb: np.ndarray) -> np.ndarray:
    src = np.array(original_img.convert("RGB"), dtype=np.float32)
    gray = np.dot(src, np.array([0.299, 0.587, 0.114], dtype=np.float32))
    dist_bg = np.sqrt(np.sum((src - bg_rgb.reshape(1, 1, 3)) ** 2, axis=2))
    edge_strength = estimate_edge_strength(gray)
    bg_brightness = float(np.mean(bg_rgb))
    darkness = np.clip(bg_brightness - gray, 0.0, 255.0)
    saturation = np.max(src, axis=2) - np.min(src, axis=2)

    dark_alpha = np.clip((darkness - 18.0) / 42.0, 0.0, 1.0)
    color_alpha = np.clip((dist_bg - 14.0) / 34.0, 0.0, 1.0) * np.clip((saturation - 10.0) / 42.0, 0.0, 1.0)
    edge_dark_alpha = np.clip((edge_strength - 3.5) / 10.0, 0.0, 1.0) * np.clip((darkness - 20.0) / 30.0, 0.0, 1.0)

    alpha = np.maximum.reduce([dark_alpha, color_alpha, edge_dark_alpha])
    support = _neighbor_sum(alpha > 0.18, radius=1)
    alpha = np.where((alpha > 0.10) & (support >= 2), alpha, 0.0)
    return np.clip(alpha * 255.0, 0, 255).astype(np.uint8)

def filter_artwork_restoration_mask(base_alpha: np.ndarray,
                                    candidate_alpha: np.ndarray,
                                    darkness: np.ndarray,
                                    edge_strength: np.ndarray,
                                    dist_bg: np.ndarray,
                                    saturation: np.ndarray) -> np.ndarray:
    candidate = candidate_alpha > 18
    if not np.any(candidate):
        return candidate

    visited = np.zeros(candidate.shape, dtype=bool)
    keep = np.zeros(candidate.shape, dtype=bool)
    h, w = candidate.shape
    starts = np.argwhere(candidate)

    for sy, sx in starts:
        if visited[sy, sx]:
            continue

        stack = [(int(sy), int(sx))]
        coords = []
        size = 0
        overlap = 0
        strong_dark = 0
        dark_edges = 0
        colored = 0
        faint = 0

        while stack:
            y, x = stack.pop()
            if y < 0 or x < 0 or y >= h or x >= w:
                continue
            if visited[y, x] or not candidate[y, x]:
                continue
            visited[y, x] = True
            coords.append((y, x))
            size += 1

            if base_alpha[y, x] > 24:
                overlap += 1
            if darkness[y, x] >= 44:
                strong_dark += 1
            if darkness[y, x] >= 28 and edge_strength[y, x] >= 4.5:
                dark_edges += 1
            if saturation[y, x] >= 28 and dist_bg[y, x] >= 18:
                colored += 1
            if darkness[y, x] < 26 and saturation[y, x] < 18:
                faint += 1

            stack.append((y - 1, x))
            stack.append((y + 1, x))
            stack.append((y, x - 1))
            stack.append((y, x + 1))
            stack.append((y - 1, x - 1))
            stack.append((y - 1, x + 1))
            stack.append((y + 1, x - 1))
            stack.append((y + 1, x + 1))

        keep_component = (
            overlap >= max(45, int(size * 0.03)) or
            strong_dark >= max(20, int(size * 0.10)) or
            dark_edges >= max(24, int(size * 0.22)) or
            colored >= max(18, int(size * 0.16))
        )

        # Componentes muito grandes e apagados quase sempre sao o fundo decorativo.
        if size >= 1800 and overlap < int(size * 0.025) and strong_dark < int(size * 0.03):
            keep_component = False
        if faint >= int(size * 0.72) and strong_dark < int(size * 0.04) and colored < int(size * 0.05):
            keep_component = False

        if keep_component:
            for y, x in coords:
                keep[y, x] = True

    return keep

def reforcar_detalhes_de_arte(original_img: Image.Image, result_img: Image.Image,
                              bg_rgb: np.ndarray, distance_threshold=28.0) -> Image.Image:
    src = np.array(original_img.convert("RGB"), dtype=np.float32)
    arr = np.array(result_img.convert("RGBA"), dtype=np.float32)
    base_alpha = arr[..., 3].copy()
    alpha = base_alpha.copy()

    dist_bg = np.sqrt(np.sum((src - bg_rgb.reshape(1, 1, 3)) ** 2, axis=2))
    gray = np.dot(src, np.array([0.299, 0.587, 0.114], dtype=np.float32))
    edge_strength = estimate_edge_strength(gray)
    saturation = np.max(src, axis=2) - np.min(src, axis=2)
    bg_brightness = float(np.mean(bg_rgb))
    darkness = np.clip(bg_brightness - gray, 0.0, 255.0)

    artwork_alpha = build_artwork_protection_alpha(original_img, bg_rgb)
    filtered_restore = filter_artwork_restoration_mask(
        base_alpha, artwork_alpha, darkness, edge_strength, dist_bg, saturation
    )
    alpha = np.where(filtered_restore, np.maximum(alpha, artwork_alpha.astype(np.float32)), alpha)

    near_subject = _neighbor_sum(base_alpha > 16, radius=2) > 0
    dark_text = (darkness >= 36) & (edge_strength >= 3.8)
    colored_detail = (saturation >= 26) & (dist_bg >= 18)
    restore_mask = (
        (dark_text | colored_detail | near_subject) &
        (dist_bg >= distance_threshold * 0.85) &
        (edge_strength >= 3.0) &
        (alpha < 235)
    )
    restored_alpha = np.clip(
        (dist_bg - distance_threshold * 0.85) * 4.2 +
        edge_strength * 16.0 +
        np.clip(darkness - 22.0, 0.0, 120.0) * 1.4,
        0, 255
    )
    alpha = np.where(restore_mask, np.maximum(alpha, restored_alpha), alpha)

    decorative_bg = (
        (darkness < 28) &
        (saturation < 22) &
        (edge_strength < 7.5) &
        (dist_bg < 34)
    )
    alpha = np.where(decorative_bg & ~dark_text & ~colored_detail, np.minimum(alpha, base_alpha), alpha)

    clean_bg = (dist_bg < 6.0) & (edge_strength < 1.5)
    alpha = np.where(clean_bg, 0.0, alpha)

    arr[..., 3] = alpha
    return sanitizar_rgb_transparente(
        Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    )

def refinar_alpha_com_fundo(original_img: Image.Image, result_img: Image.Image,
                            bg_rgb: np.ndarray, edge_radius=3,
                            low=20.0, high=100.0) -> Image.Image:
    src = np.array(original_img.convert("RGB"), dtype=np.float32)
    arr = np.array(result_img.convert("RGBA"), dtype=np.float32)
    alpha = arr[...,3]

    borda = _mask_borda_alpha(alpha, edge_radius=edge_radius, alpha_cutoff=252)
    opaque_support = _neighbor_sum(alpha > 200, radius=1)
    semi_support = _neighbor_sum(alpha > 24, radius=1)

    dist_bg = np.sqrt(np.sum((src - bg_rgb.reshape(1, 1, 3)) ** 2, axis=2))
    target = np.clip((dist_bg - low) / max(high - low, 1.0), 0, 1)
    target = np.power(target, 0.82) * 255.0

    # Refinamento focado em pixels da borda onde a cor original ainda parece
    # próxima do fundo, o que costuma gerar esse halo branco nos fios.
    refine_mask = borda & ((alpha < 250) | (opaque_support <= 7))
    alpha = np.where(refine_mask, np.minimum(alpha, target), alpha)

    # Restos muito claros e soltos viram praticamente transparentes.
    loose_bg = borda & (dist_bg < low + 8.0) & (semi_support <= 4)
    alpha = np.where(loose_bg, alpha * 0.03, alpha)

    # Se ainda parecer fundo mas tiver um pouco mais de suporte, reduz bastante.
    light_bg = borda & (dist_bg < low + 22.0) & (opaque_support <= 5)
    alpha = np.where(light_bg, alpha * 0.25, alpha)

    arr[...,3] = alpha
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def proteger_fios_de_cabelo(original_img: Image.Image, result_img: Image.Image,
                            bg_rgb: np.ndarray, edge_radius=3) -> Image.Image:
    src = np.array(original_img.convert("RGB"), dtype=np.float32)
    arr = np.array(result_img.convert("RGBA"), dtype=np.float32)
    alpha = arr[..., 3].copy()

    borda = _mask_borda_alpha(alpha, edge_radius=edge_radius, alpha_cutoff=252)
    semi_support = _neighbor_sum(alpha > 22, radius=1)
    opaque_support = _neighbor_sum(alpha > 188, radius=1)
    dist_bg = np.sqrt(np.sum((src - bg_rgb.reshape(1, 1, 3)) ** 2, axis=2))
    saturation = np.max(src, axis=2) - np.min(src, axis=2)
    gray = np.dot(src, np.array([0.299, 0.587, 0.114], dtype=np.float32))
    edge_strength = estimate_edge_strength(gray)

    warm_strands = (
        (src[..., 0] >= src[..., 1] - 8) &
        (src[..., 1] >= src[..., 2] - 12) &
        (src[..., 0] >= 52)
    )
    strand_mask = (
        borda &
        (alpha >= 10) &
        (alpha < 246) &
        (semi_support >= 1) &
        (opaque_support <= 7) &
        (edge_strength >= 2.2) &
        ((saturation >= 14) | warm_strands) &
        (dist_bg >= 15.0)
    )
    restored_alpha = np.clip(
        alpha +
        np.clip(dist_bg - 15.0, 0.0, 80.0) * 2.7 +
        np.clip(edge_strength - 2.0, 0.0, 12.0) * 8.0 +
        np.clip(saturation - 10.0, 0.0, 70.0) * 0.55,
        0, 255
    )
    alpha = np.where(strand_mask, np.maximum(alpha, restored_alpha), alpha)

    loose_bg = borda & (dist_bg < 14.0) & (semi_support <= 2) & (opaque_support <= 1)
    alpha = np.where(loose_bg, alpha * 0.08, alpha)

    arr[..., 3] = alpha
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

def descontaminar_bordas(img: Image.Image, bg_rgb: np.ndarray,
                         edge_radius=2, similarity_threshold=42.0) -> Image.Image:
    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    rgb = arr[...,:3]
    alpha = arr[...,3]
    a_norm = alpha / 255.0

    borda = _mask_borda_alpha(alpha, edge_radius=edge_radius, alpha_cutoff=250)
    dist = np.sqrt(np.sum((rgb - bg_rgb.reshape(1, 1, 3)) ** 2, axis=2))
    bg_like = dist < similarity_threshold

    semi_support = _neighbor_sum(alpha > 24, radius=1)
    opaque_support = _neighbor_sum(alpha > 200, radius=1)

    fringe = borda & bg_like & ((semi_support <= 7) | (alpha < 235))
    loose = fringe & (opaque_support <= 3)

    safe_alpha = np.maximum(a_norm, 0.08)
    descontaminado = (rgb - bg_rgb.reshape(1, 1, 3) * (1.0 - safe_alpha[...,None])) / safe_alpha[...,None]
    descontaminado = np.clip(descontaminado, 0, 255)
    mix = np.clip((similarity_threshold - dist) / max(similarity_threshold, 1.0), 0, 1)

    rgb = np.where(fringe[...,None], rgb*(1.0-mix[...,None]) + descontaminado*mix[...,None], rgb)

    # Pixels muito parecidos com o fundo e com pouco suporte costumam ser restos do fundo.
    alpha = np.where(loose, alpha * 0.10, alpha)
    alpha = np.where(fringe & (alpha < 240), alpha * (1.0 - 0.72*mix), alpha)

    arr[...,:3] = rgb
    arr[...,3] = alpha
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def recolorir_borda_por_vizinhos(img: Image.Image, edge_radius=2, sample_radius=2,
                                 alpha_min=1, alpha_max=245,
                                 support_alpha=220) -> Image.Image:
    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    rgb = arr[..., :3]
    alpha = arr[..., 3]

    borda = _mask_borda_alpha(alpha, edge_radius=edge_radius, alpha_cutoff=250)
    alvo = borda & (alpha > alpha_min) & (alpha < alpha_max)
    suporte = alpha >= support_alpha

    if not np.any(alvo) or not np.any(suporte):
        return sanitizar_rgb_transparente(Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA"))

    pad = max(1, int(sample_radius))
    h, w = alpha.shape
    padded_rgb = np.pad(rgb, ((pad, pad), (pad, pad), (0, 0)), mode="edge")
    padded_support = np.pad(suporte.astype(np.float32), ((pad, pad), (pad, pad)), mode="constant")

    acumulado = np.zeros_like(rgb)
    pesos = np.zeros((h, w), dtype=np.float32)

    for dy in range(-pad, pad + 1):
        for dx in range(-pad, pad + 1):
            if dx == 0 and dy == 0:
                continue
            ys = dy + pad
            xs = dx + pad
            distancia = max((dx * dx + dy * dy) ** 0.5, 1.0)
            peso = 1.0 / distancia
            suporte_local = padded_support[ys:ys + h, xs:xs + w] * peso
            acumulado += padded_rgb[ys:ys + h, xs:xs + w] * suporte_local[..., None]
            pesos += suporte_local

    valido = pesos > 0
    media_vizinhos = np.where(valido[..., None], acumulado / np.maximum(pesos[..., None], 1e-6), rgb)

    brilho = np.mean(rgb, axis=2)
    saturacao = np.max(rgb, axis=2) - np.min(rgb, axis=2)
    vies_branco = np.clip((brilho - 145.0) / 110.0, 0, 1) * np.clip((85.0 - saturacao) / 85.0, 0, 1)
    transparencia = 1.0 - (alpha / 255.0)
    forca = np.clip(0.18 + 0.52 * transparencia + 0.35 * vies_branco, 0.0, 0.88)

    aplicar = alvo & valido
    rgb = np.where(
        aplicar[..., None],
        rgb * (1.0 - forca[..., None]) + media_vizinhos * forca[..., None],
        rgb
    )

    arr[..., :3] = rgb
    return sanitizar_rgb_transparente(
        Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")
    )

def limpar_bordas(img: Image.Image, threshold=225, edge_radius=2) -> Image.Image:
    arr = np.array(img.convert("RGBA"), dtype=np.float32)
    r,g,b,a = arr[...,0],arr[...,1],arr[...,2],arr[...,3]
    brilho = (r+g+b)/3.0
    saturacao = np.max(arr[...,:3], axis=2) - np.min(arr[...,:3], axis=2)
    borda = _mask_borda_alpha(a, edge_radius=edge_radius, alpha_cutoff=245)
    semi_support = _neighbor_sum(a > 20, radius=1)
    opaque_support = _neighbor_sum(a > 180, radius=1)

    # Pontinhos claros perdidos no cabelo/franja costumam aparecer quase isolados.
    pontos_soltos = (
        borda &
        (brilho > max(threshold - 15, 215)) &
        (saturacao < 95) &
        (semi_support <= 3)
    )
    a = np.where(pontos_soltos, 0, a)

    mask = borda & (brilho > threshold) & (saturacao < 70) & (a > 0)
    fator = np.clip((brilho - threshold)/max(255.0 - threshold, 1.0), 0, 1)

    # Remove halo branco fino com mais força quando o pixel ainda nao tem
    # suporte opaco suficiente, evitando comer cabelo mais "cheio".
    fringe_mask = (
        borda &
        (brilho > max(threshold - 12, 205)) &
        (saturacao < 105) &
        (opaque_support <= 6) &
        (a < 245)
    )
    fringe_strength = np.clip(
        (brilho - max(threshold - 18, 195)) / max(255.0 - max(threshold - 18, 195), 1.0),
        0, 1
    )

    novo_alpha = np.where(mask, a*(1.0-fator), a)
    novo_alpha = np.where(fringe_mask, np.minimum(novo_alpha, a*(1.0 - 0.92*fringe_strength)), novo_alpha)
    arr[...,3] = novo_alpha

    # Escurece levemente a cor contaminada da borda para reduzir branco residual.
    fringe_dark = fringe_mask[...,None]
    escurecer = (1.0 - 0.28*fringe_strength)[...,None]
    arr[...,:3] = np.where(fringe_dark, arr[...,:3] * escurecer, arr[...,:3])
    return Image.fromarray(np.clip(arr,0,255).astype(np.uint8))

def suavizar_serrilhado_alpha(img: Image.Image, edge_radius=1, blur_radius=0.75) -> Image.Image:
    rgba = img.convert("RGBA")
    arr = np.array(rgba, dtype=np.float32)
    alpha = arr[..., 3]
    if np.max(alpha) <= 0:
        return rgba

    edge_mask = _mask_borda_alpha(alpha, edge_radius=edge_radius, alpha_cutoff=252)
    support = _neighbor_sum(alpha > 14, radius=1)
    edge_mask = edge_mask & (support >= 1)
    if not np.any(edge_mask):
        return rgba

    blurred_rgba = np.array(rgba.filter(ImageFilter.GaussianBlur(blur_radius)).convert("RGBA"), dtype=np.float32)
    blurred_alpha = blurred_rgba[..., 3]
    mixed_alpha = np.clip(alpha * 0.38 + blurred_alpha * 0.62, 0, 255)
    arr[..., 3] = np.where(edge_mask, mixed_alpha, alpha)

    color_mix = arr[..., :3] * 0.62 + blurred_rgba[..., :3] * 0.38
    arr[..., :3] = np.where(edge_mask[..., None], color_mix, arr[..., :3])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

def suavizar_borda_humana(original_img: Image.Image, result_img: Image.Image,
                          bg_rgb: np.ndarray, edge_radius=2) -> Image.Image:
    src = np.array(original_img.convert("RGB"), dtype=np.float32)
    rgba = result_img.convert("RGBA")
    arr = np.array(rgba, dtype=np.float32)
    alpha = arr[..., 3]
    if np.max(alpha) <= 0:
        return rgba

    dist_bg = np.sqrt(np.sum((src - bg_rgb.reshape(1, 1, 3)) ** 2, axis=2))
    gray = np.dot(src, np.array([0.299, 0.587, 0.114], dtype=np.float32))
    edge_strength = estimate_edge_strength(gray)
    saturation = np.max(src, axis=2) - np.min(src, axis=2)
    r, g, b = src[..., 0], src[..., 1], src[..., 2]
    skin_like = (
        (r > 92) &
        (g > 40) &
        (b > 20) &
        (r > g) &
        (g > b - 10) &
        ((np.max(src, axis=2) - np.min(src, axis=2)) > 12)
    )

    edge_mask = _mask_borda_alpha(alpha, edge_radius=edge_radius, alpha_cutoff=252)
    support = _neighbor_sum(alpha > 20, radius=1)
    target_mask = (
        edge_mask &
        (support >= 1) &
        ((skin_like & (dist_bg >= 14)) | ((saturation < 38) & (dist_bg >= 16))) &
        (edge_strength <= 10.5)
    )
    if not np.any(target_mask):
        return rgba

    alpha_img = Image.fromarray(alpha.astype(np.uint8), "L")
    softened = alpha_img.filter(ImageFilter.GaussianBlur(1.05))
    softened = softened.filter(ImageFilter.MaxFilter(3))
    soft_arr = np.array(softened, dtype=np.float32)

    blend = np.clip((12.0 - edge_strength) / 12.0, 0.18, 0.72)
    mixed_alpha = np.clip(alpha * (1.0 - blend) + soft_arr * blend, 0, 255)
    arr[..., 3] = np.where(target_mask, mixed_alpha, alpha)

    soft_rgba = np.array(rgba.filter(ImageFilter.GaussianBlur(0.65)).convert("RGBA"), dtype=np.float32)
    arr[..., :3] = np.where(target_mask[..., None], arr[..., :3] * 0.72 + soft_rgba[..., :3] * 0.28, arr[..., :3])
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGBA")

def erosao_alpha(img: Image.Image, px: int) -> Image.Image:
    if px <= 0: return img
    arr = np.array(img.convert("RGBA"))
    alpha = Image.fromarray(arr[...,3], "L")
    for _ in range(px):
        alpha = alpha.filter(ImageFilter.MinFilter(3))
    arr[...,3] = np.array(alpha)
    return Image.fromarray(arr)

def processing_profile(width: int, height: int, threshold: int):
    area = width * height
    min_side = min(width, height)

    erode_size = 3
    clean_threshold = threshold
    edge_radius = 2

    if min_side <= 320 or area <= 150_000:
        erode_size = 0
        clean_threshold = max(threshold, 245)
        edge_radius = 1
    elif min_side <= 640 or area <= 500_000:
        erode_size = 1
        clean_threshold = max(threshold, 238)
        edge_radius = 1
    elif min_side <= 900 or area <= 1_000_000:
        erode_size = 2
        clean_threshold = max(threshold, 230)

    return erode_size, clean_threshold, edge_radius


def sugerir_limiar_branco(img: Image.Image) -> int:
    """Analisa o fundo da imagem e retorna o limiar de branco ideal para a pipeline.

    Lógica:
    - Fundo muito escuro          → 252  (sem bordas brancas para limpar)
    - Fundo colorido saturado     → 245  (o filtro de cor cuida; branco é irrelevante)
    - Fundo cinza médio           → 230  (limpeza moderada)
    - Fundo quase-branco / branco → 212–225  (limpeza agressiva de halos)
    """
    bg_rgb = estimate_background_color(img)
    bg_brightness = float(np.mean(bg_rgb))
    bg_saturation = float(np.max(bg_rgb) - np.min(bg_rgb))

    if bg_brightness < 60:
        return 252                                     # fundo escuro
    if bg_saturation > 65:
        return 245                                     # fundo colorido saturado
    if bg_brightness > 225:
        # Branco puro → limiar mais baixo para pegar halos
        return max(210, int(255 - (bg_brightness - 205) * 2.0))
    # Escala linear entre cinza médio e quase-branco
    return int(248 - (bg_brightness - 60) * 0.12)


def detectar_paleta_fundo(img: Image.Image, n_colors: int = 5) -> list:
    """Detecta as cores dominantes do fundo usando APENAS os pixels mais externos da borda.

    Usa somente as 4 fileiras mais externas (não 24px) para evitar capturar
    cabelo, roupa ou pele do sujeito que esteja próximo à borda.
    Em seguida filtra outliers: mantém apenas pixels dentro de ±45 da mediana
    da borda (exclui pixels isolados do sujeito que vazaram para a borda).
    """
    arr = np.array(img.convert("RGB"))
    h, w = arr.shape[:2]
    # Borda muito fina — apenas pixels claramente de fundo
    border_px = max(3, min(5, h // 25, w // 25))
    pieces = [
        arr[:border_px, :].reshape(-1, 3),
        arr[h - border_px:, :].reshape(-1, 3),
        arr[:, :border_px].reshape(-1, 3),
        arr[:, w - border_px:].reshape(-1, 3),
    ]
    pixels = np.concatenate(pieces, axis=0).astype(np.float32)
    if len(pixels) == 0:
        return []

    # Filtra outliers: mantém apenas pixels próximos à cor mediana da borda.
    # Isso remove pixels de cabelo/roupa que aparecem na extremidade da imagem.
    median_color = np.median(pixels, axis=0)
    dist_from_median = np.sqrt(np.sum((pixels - median_color) ** 2, axis=1))
    thr = max(float(np.percentile(dist_from_median, 70)), 20.0)
    thr = min(thr, 55.0)   # nunca mais de 55 — força a cluster ficar apertado
    filtered = pixels[dist_from_median <= thr]
    if len(filtered) < 8:
        filtered = pixels   # fallback se filtragem for demasiado agressiva

    n = min(n_colors, len(filtered))
    rng = np.random.default_rng(42)
    idx = rng.choice(len(filtered), n, replace=False)
    centers = filtered[idx].copy()

    for _ in range(40):
        diffs = filtered[:, None, :] - centers[None, :, :]
        labels = np.argmin(np.sum(diffs ** 2, axis=2), axis=1)
        new_centers = np.array([
            filtered[labels == k].mean(axis=0) if (labels == k).any() else centers[k]
            for k in range(n)
        ])
        if np.allclose(centers, new_centers, atol=0.5):
            break
        centers = new_centers

    counts = np.bincount(labels, minlength=n)
    order = np.argsort(-counts)
    return [
        (int(np.clip(centers[k, 0], 0, 255)),
         int(np.clip(centers[k, 1], 0, 255)),
         int(np.clip(centers[k, 2], 0, 255)))
        for k in order if counts[k] > 0
    ][:n_colors]


def aplicar_color_key(result_rgba: Image.Image, src_rgb: Image.Image,
                      bg_colors: list, tolerance: int = 35,
                      suppress_spill: bool = True) -> Image.Image:
    """Pós-processamento: apaga pixels residuais que correspondam a cores de fundo conhecidas.

    Usa a imagem ORIGINAL (src_rgb) como referência de cor — não o resultado —
    para identificar com precisão quais pixels eram fundo.
    """
    if not bg_colors:
        return result_rgba

    arr_r = np.array(result_rgba.convert("RGBA"), dtype=np.float32)
    arr_o = np.array(src_rgb.convert("RGB"), dtype=np.float32)
    tol = float(max(tolerance, 1))

    # Máscara de pixels semi-transparentes: rembg já os marcou como "borda de transição".
    # Pixels TOTALMENTE opacos (alpha >= 215) são provavelmente sujeito real (roupa, pele)
    # e só devem ser tocados pelo blob-cleanup com condições muito restritas.
    semi_only = arr_r[:, :, 3] < 215   # proteção: não toca totalmente opacos

    for (cr, cg, cb) in bg_colors:
        c = np.array([cr, cg, cb], dtype=np.float32)
        dist = np.sqrt(np.sum((arr_o - c) ** 2, axis=2))

        # Remoção dura — apenas pixels JÁ semi-transparentes perto do fundo
        hard = (dist <= tol * 0.55) & (arr_r[:, :, 3] > 20) & semi_only
        arr_r[hard, 3] = 0.0

        # Transição suave — idem, apenas semi-transparentes
        soft = (dist > tol * 0.55) & (dist <= tol) & (arr_r[:, :, 3] > 20) & semi_only
        if soft.any():
            ratio = (dist[soft] - tol * 0.55) / (tol * 0.45 + 1e-6)
            ratio = np.clip(ratio, 0.0, 1.0)
            arr_r[soft, 3] = np.minimum(arr_r[soft, 3], ratio * 255.0)

        # Supressão de spill: decontamina pixels semitransparentes com tinta do fundo
        if suppress_spill:
            semi = (arr_r[:, :, 3] > 8) & (arr_r[:, :, 3] < 210)
            if semi.any():
                sy, sx = np.where(semi)
                dist_s = np.sqrt(np.sum((arr_o[sy, sx] - c) ** 2, axis=1))
                close = dist_s < tol * 1.6
                if close.any():
                    ky, kx = sy[close], sx[close]
                    alpha_k = arr_r[ky, kx, 3] / 255.0
                    contamination = np.clip(1.0 - alpha_k, 0.0, 0.88) * 0.60
                    decontam = arr_r[ky, kx, :3] - c * contamination[:, None]
                    arr_r[ky, kx, :3] = np.clip(decontam, 0.0, 255.0)

    # ── Blob cleanup: pixels opacos de borda com cor de fundo no original ─────────────────
    # Única situação onde tocamos pixels opacos: estão completamente encostados em
    # transparent (≥3 vizinhos transparentes) E a cor original era muito próxima do fundo.
    alpha_now = arr_r[:, :, 3]
    transparent_now = alpha_now < 30
    trans_pad = np.pad(transparent_now.astype(np.uint8), 1, mode='constant')
    neighbors_transparent = (
        trans_pad[:-2, 1:-1] + trans_pad[2:, 1:-1] +
        trans_pad[1:-1, :-2] + trans_pad[1:-1, 2:]
    )
    for (cr, cg, cb) in bg_colors:
        c = np.array([cr, cg, cb], dtype=np.float32)
        dist_o = np.sqrt(np.sum((arr_o - c) ** 2, axis=2))
        # Exige 3+ vizinhos transparentes (mais restritivo) para pixels totalmente opacos
        residue = (alpha_now > 60) & (dist_o <= tol * 0.85) & (neighbors_transparent >= 3)
        arr_r[residue, 3] = 0.0

    # ── Erosão iterativa da franja — apenas pixels SEMI-TRANSPARENTES de borda ───────────
    # A franja residual ao redor do cabelo é semi-transparente (rembg já a marcou assim).
    # Verificamos a cor do RESULTADO (não original) porque esses pixels continuam
    # visivelmente cor-de-fundo mesmo depois dos passes anteriores.
    # Restringindo a alpha < 215 garantimos que roupa e pele opacos nunca são tocados.
    tol_result = max(tol * 1.45, 55.0)
    for _ in range(6):          # 6 passes são suficientes para a franja típica
        alpha_iter = arr_r[:, :, 3]
        transp_iter = alpha_iter < 25

        tp = np.pad(transp_iter.astype(np.uint8), 1, mode='constant')
        near_transp = (
            tp[:-2, 1:-1] + tp[2:, 1:-1] + tp[1:-1, :-2] + tp[1:-1, 2:]
        ) > 0

        removed_any = False
        for (cr, cg, cb) in bg_colors:
            c = np.array([cr, cg, cb], dtype=np.float32)
            dist_result = np.sqrt(np.sum((arr_r[:, :, :3] - c) ** 2, axis=2))
            # Somente semi-transparentes na borda — NUNCA pixels totalmente opacos
            remove = (near_transp & (dist_result <= tol_result)
                      & (arr_r[:, :, 3] > 15) & (arr_r[:, :, 3] < 215))
            if remove.any():
                arr_r[remove, 3] = 0.0
                removed_any = True

        if not removed_any:
            break

    return sanitizar_rgb_transparente(
        Image.fromarray(np.clip(arr_r, 0, 255).astype(np.uint8), "RGBA")
    )


def remover_fundo_sticker(img: Image.Image, tolerance: int = 35, edge_barrier: float = 20.0) -> Image.Image:
    """
    Remove apenas o fundo EXTERNO usando flood fill morfológico com barreira de gradiente.

    Estratégia:
      1. Pixels similares à cor do fundo E sem transição brusca de cor são "inundáveis".
      2. Pixels com forte variação de cor nos vizinhos (bordas do design) bloqueiam
         a propagação — isso impede que o flood fill cruze o contorno do sticker e
         entre nas áreas brancas internas.
      3. Após o flood fill, pixels internos isolados que ficaram transparentes são
         restaurados (ex: pontos brancos de halftone completamente cercados pelo design).
    """
    img_rgba = img.convert("RGBA")
    arr = np.array(img_rgba, dtype=np.uint8)
    h, w = arr.shape[:2]

    # ── Cor do fundo (mediana das bordas) ──────────────────────
    edge_pixels = np.concatenate([
        arr[0, :, :3],
        arr[h - 1, :, :3],
        arr[:, 0, :3],
        arr[:, w - 1, :3],
    ], axis=0).astype(np.float32)
    bg_color = np.median(edge_pixels, axis=0)

    # ── Máscara de similaridade com o fundo ────────────────────
    rgb = arr[:, :, :3].astype(np.float32)
    dist = np.sqrt(np.sum((rgb - bg_color) ** 2, axis=2))
    similar = dist <= float(tolerance)

    # ── Barreira de gradiente ───────────────────────────────────
    # Pixels com grande variação de cor em relação aos vizinhos são bordas
    # do design e bloqueiam o flood fill, protegendo as áreas internas.
    gray = np.dot(rgb, np.array([0.299, 0.587, 0.114], dtype=np.float32))
    edge_str = estimate_edge_strength(gray)
    barrier = edge_str >= edge_barrier  # transição brusca = barreira

    # Inundável = similar ao fundo E não é uma barreira de borda
    floodable = similar & ~barrier

    # ── Flood fill a partir das 4 bordas ───────────────────────
    connected = np.zeros((h, w), dtype=bool)
    connected[0, :]     |= floodable[0, :]
    connected[h - 1, :] |= floodable[h - 1, :]
    connected[:, 0]     |= floodable[:, 0]
    connected[:, w - 1] |= floodable[:, w - 1]

    changed = True
    while changed:
        prev = connected.copy()
        exp = connected.copy()
        exp[1:, :]  |= connected[:-1, :]
        exp[:-1, :] |= connected[1:, :]
        exp[:, 1:]  |= connected[:, :-1]
        exp[:, :-1] |= connected[:, 1:]
        connected = exp & floodable
        changed = not np.array_equal(connected, prev)

    result = arr.copy()
    result[connected, 3] = 0

    # ── Restaurar ilhas transparentes internas ──────────────────
    # Pixels transparentes que NÃO estão conectados à borda da imagem
    # são regiões internas que vazaram — restauramos com a cor original.
    alpha_after = result[:, :, 3]
    transparent = alpha_after == 0

    border_connected = np.zeros((h, w), dtype=bool)
    border_connected[0, :]     |= transparent[0, :]
    border_connected[h - 1, :] |= transparent[h - 1, :]
    border_connected[:, 0]     |= transparent[:, 0]
    border_connected[:, w - 1] |= transparent[:, w - 1]

    changed = True
    while changed:
        prev = border_connected.copy()
        exp = border_connected.copy()
        exp[1:, :]  |= border_connected[:-1, :]
        exp[:-1, :] |= border_connected[1:, :]
        exp[:, 1:]  |= border_connected[:, :-1]
        exp[:, :-1] |= border_connected[:, 1:]
        border_connected = exp & transparent
        changed = not np.array_equal(border_connected, prev)

    # Ilhas isoladas = transparentes mas NÃO conectadas à borda
    isolated = transparent & ~border_connected
    result[isolated, :] = arr[isolated, :]  # restaura cor + alpha originais

    return sanitizar_rgb_transparente(Image.fromarray(result, "RGBA"))


# ── App ──────────────────────────────────────────────────────
class App(TK_ROOT):
    def __init__(self):
        super().__init__()
        self.title("Background Remover Studio")
        self.configure(bg=BG)
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        default_w = max(1160, min(1360, sw - 120))
        default_h = max(720, min(800, sh - 150))
        self.geometry(f"{default_w}x{default_h}")
        self.minsize(min(default_w, 980), min(default_h, 660))

        from _paths import resource as _resource
        icon_path = _resource("icon.ico")
        if icon_path.exists():
            try: self.iconbitmap(str(icon_path))
            except: pass

        self._files:     list[str]              = []
        self._results:   dict[str, Image.Image] = {}
        self._retouched: dict[str, Image.Image] = {}
        self._processing = False
        self._closing = False
        self._stop_requested = threading.Event()
        self._rembg_session = None
        self._sel:       int | None             = None
        self._out_dir:   str | None             = None
        self._lang = "en"
        self._slider_label_refs = {}

        # refs para evitar GC
        self._tk_before = None
        self._tk_after  = None

        self._modo_simples = tk.BooleanVar(value=True)
        self._alpha_mat    = tk.BooleanVar(value=True)
        self._thr_main     = tk.IntVar(value=225)
        self._thr_ret      = tk.IntVar(value=225)
        self._erode_ret    = tk.IntVar(value=0)
        self._process_selected_only = tk.BooleanVar(value=False)
        self._manual_tool = tk.StringVar(value="none")
        self._brush_size = tk.IntVar(value=22)
        self._brush_shape = tk.StringVar(value="round")
        self._hair_protect = tk.BooleanVar(value=True)
        self._sticker_mode = tk.BooleanVar(value=False)
        self._color_key_tol = tk.IntVar(value=35)
        self._spill_suppress = tk.BooleanVar(value=True)
        self._detected_colors: list = []          # (r,g,b) tuples from last detection
        self._resize_enabled = tk.BooleanVar(value=False)
        self._resize_width = tk.StringVar(value="")
        self._resize_height = tk.StringVar(value="")
        self._resize_lock = tk.BooleanVar(value=True)
        self._resize_syncing = False
        self._resize_section_open = False
        self._orig_width = 0
        self._orig_height = 0
        self._preview_zoom = 1.0
        self._zoom_text = tk.StringVar(value="100%")
        self._resolution_text = tk.StringVar(value=self._t("no_image"))
        self._view_mode = tk.StringVar(value="split")
        self._export_format = tk.StringVar(value="")
        self._export_format_key = "png"
        self._preview_bg_cache: dict[tuple[int, int], ImageTk.PhotoImage] = {}
        self._file_thumb_cache: dict[str, ImageTk.PhotoImage] = {}
        self._file_row_refs: dict[str, dict[str, object]] = {}
        self._failed_files: set[str] = set()
        self._hover_file_path: str | None = None
        self._loading_cards: set[tk.Frame] = set()
        self._loading_anim_job = None
        self._loading_phase = 0
        self._rt_card_b = None
        self._rt_card_a = None
        self._mousewheel_target = None
        self._preview_redraw_job = None
        self._manual_drag_last = None
        self._manual_original_path = None
        self._manual_original_rgba = None
        self._manual_history: dict[str, list[Image.Image]] = {}
        self._manual_history_index: dict[str, int] = {}
        self._controls_collapsed = False
        self._quick_tools_open = False
        self._preview_nav_mode = False
        self._split_ratio = 0.5
        self._resize_width.trace_add("write", self._on_resize_width_change)
        self._resize_height.trace_add("write", self._on_resize_height_change)

        self._build()
        self._sync_export_combo()
        self._toggle_modo()
        self.bind_all("<MouseWheel>", self._on_mousewheel_target, add="+")
        self.bind("<Configure>", self._on_root_configure, add="+")
        self.bind_all("<Control-z>", self._undo_shortcut, add="+")
        self.bind_all("<Control-y>", self._redo_shortcut, add="+")
        self.bind_all("<Control-Shift-Z>", self._redo_shortcut, add="+")
        self.protocol("WM_DELETE_WINDOW", self._close_app)
        self._center()
        self._setup_drag_and_drop()
        self._load_model()

    # ── Modelo ────────────────────────────────────────────────
    def _load_model(self):
        self._set_status("Loading AI engine... the first launch can take a little longer.", DIM)
        self._set_glow_button_loading(self._btn_run, True, self._t("loading_model"))
        def _t():
            global rembg_remove, rembg_pronto, rembg_new_session
            try:
                from rembg import remove as rm, new_session as new_session_factory
                rembg_remove = rm
                rembg_new_session = new_session_factory
                self._rembg_session = new_session_factory()
                rembg_pronto = True
                if self._stop_requested.is_set():
                    return
                self.after(0, self._model_ready)
            except ImportError:
                if self._stop_requested.is_set():
                    return
                self.after(0, lambda: (
                    self._set_glow_button_text(self._btn_run, self._t("unavailable")),
                    self._set_glow_button_enabled(self._btn_run, False),
                    self._set_status(self._t("startup_error"), ERROR)
                ))
        threading.Thread(target=_t, daemon=True).start()

    def _model_ready(self):
        if self._stop_requested.is_set():
            return
        self._set_status(self._t("ready_status"), SUCCESS)
        self._set_glow_button_loading(self._btn_run, False)
        self._set_glow_button_enabled(self._btn_run, True)

    # ── Build UI ──────────────────────────────────────────────
    def _build(self):
        s = ttk.Style(self)
        s.theme_use("clam")
        s.configure("Studio.Horizontal.TProgressbar", troughcolor=CARD2,
                    background=ACCENT, darkcolor=ACCENT,
                    lightcolor=ACCENT, borderwidth=0)
        s.configure("Studio.Vertical.TScrollbar", troughcolor=CARD2,
                    background=CARD, darkcolor=CARD, lightcolor=CARD,
                    bordercolor=CARD2, arrowcolor=SOFT_TEXT, gripcount=0)
        s.configure("Studio.TNotebook", background=BG, borderwidth=0)
        s.configure("Studio.TNotebook.Tab", background=CARD2, foreground=DIM,
                    padding=[16,8], font=("Segoe UI",9,"bold"), borderwidth=0)
        s.map("Studio.TNotebook.Tab",
              background=[("selected", CARD)],
              foreground=[("selected", ACCENT_CYAN)])

        s.configure("Studio.TCombobox",
                    fieldbackground=CARD2,
                    background=CARD2,
                    foreground=TEXT,
                    arrowcolor=DIM,
                    bordercolor=BORDER,
                    lightcolor=BORDER,
                    darkcolor=BORDER)
        s.map("Studio.TCombobox",
              fieldbackground=[("readonly", CARD2)],
              foreground=[("readonly", TEXT)],
              background=[("readonly", CARD2)],
              selectbackground=[("readonly", ACCENT)],
              selectforeground=[("readonly", TEXT)])
        self.option_add("*TCombobox*Listbox.background", CARD2)
        self.option_add("*TCombobox*Listbox.foreground", TEXT)
        self.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
        self.option_add("*TCombobox*Listbox.selectForeground", TEXT)

        shell = tk.Frame(self, bg=BG, padx=14, pady=14)
        shell.pack(fill="both", expand=True)
        self._shell = shell
        shell.columnconfigure(0, weight=0, minsize=220)
        shell.columnconfigure(1, weight=1, minsize=420)
        shell.columnconfigure(2, weight=0, minsize=286)
        shell.rowconfigure(1, weight=1)

        top = tk.Frame(shell, bg=TOP_BG, padx=24, pady=18,
                       highlightthickness=1, highlightbackground=BORDER)
        top.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0,18))
        title_wrap = tk.Frame(top, bg=TOP_BG)
        title_wrap.pack(side="left")
        self._lbl_title = tk.Label(title_wrap, text=self._t("header_title"),
                                   font=("Segoe UI",24,"bold"), bg=TOP_BG, fg=TEXT)
        self._lbl_title.pack(anchor="w")
        self._lbl_subtitle = tk.Label(title_wrap, text=self._t("header_subtitle"),
                                      font=("Segoe UI",10), bg=TOP_BG, fg=DIM)
        self._lbl_subtitle.pack(anchor="w", pady=(4,0))

        top_actions = tk.Frame(top, bg=TOP_BG)
        top_actions.pack(side="right")

        lang_wrap = tk.Frame(top_actions, bg=TOP_BG, padx=10, pady=8,
                             highlightthickness=1, highlightbackground=BORDER_SOFT)
        lang_wrap.pack(side="left", padx=(0,12))
        self._btn_lang_en = self._mkbtn(lang_wrap, "EN", lambda: self._set_language("en"),
                                        bg=CARD2, hover="#263446", pady=4,
                                        font=("Segoe UI",9,"bold"))
        self._btn_lang_en.pack(side="left")
        tk.Label(lang_wrap, text="|", font=("Segoe UI",9), bg=TOP_BG, fg=MUTED).pack(side="left", padx=6)
        self._btn_lang_pt = self._mkbtn(lang_wrap, "PTBR", lambda: self._set_language("pt"),
                                        bg=CARD2, hover="#263446", pady=4,
                                        font=("Segoe UI",9,"bold"))
        self._btn_lang_pt.pack(side="left")

        mode_wrap = tk.Frame(top, bg=TOP_BG, padx=14, pady=10,
                             highlightthickness=1, highlightbackground=BORDER_SOFT)
        mode_wrap.pack(in_=top_actions, side="left")
        text_wrap = tk.Frame(mode_wrap, bg=TOP_BG)
        text_wrap.pack(side="left", padx=(0,10))
        self._lbl_mode_title = tk.Label(text_wrap, text=self._t("simple_mode"), font=("Segoe UI",9,"bold"),
                                        bg=TOP_BG, fg=TEXT)
        self._lbl_mode_title.pack(anchor="w")
        self._lbl_mode_sub = tk.Label(text_wrap, text=self._t("simple_mode_sub"),
                                      font=("Segoe UI",8), bg=TOP_BG, fg=MUTED)
        self._lbl_mode_sub.pack(anchor="w", pady=(2,0))
        self._mode_toggle_canvas = tk.Canvas(
            mode_wrap, width=46, height=28, bg=TOP_BG, highlightthickness=0, bd=0, cursor="hand2"
        )
        self._mode_toggle_canvas.pack(side="right")
        text_wrap.bind("<Button-1>", self._toggle_simple_mode)
        self._lbl_mode_title.bind("<Button-1>", self._toggle_simple_mode)
        self._lbl_mode_sub.bind("<Button-1>", self._toggle_simple_mode)
        self._mode_toggle_canvas.bind("<Button-1>", self._toggle_simple_mode)
        mode_wrap.bind("<Button-1>", self._toggle_simple_mode)

        left_panel = tk.Frame(shell, bg=CARD, padx=12, pady=12, width=240,
                              highlightthickness=1, highlightbackground=BORDER)
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(0,16))
        left_panel.grid_propagate(False)
        left_panel.rowconfigure(1, weight=1)
        self._build_left(left_panel)

        center_panel = tk.Frame(shell, bg=CARD, padx=14, pady=14,
                                highlightthickness=1, highlightbackground=BORDER)
        center_panel.grid(row=1, column=1, sticky="nsew", padx=(0,16))
        center_panel.rowconfigure(2, weight=1)
        center_panel.columnconfigure(0, weight=1)
        self._build_right(center_panel)

        controls_panel = tk.Frame(shell, bg=CARD, padx=12, pady=12, width=258,
                                  highlightthickness=1, highlightbackground=BORDER)
        controls_panel.grid(row=1, column=2, sticky="nsew")
        controls_panel.grid_propagate(False)
        self._controls_panel = controls_panel
        self._build_controls(controls_panel)

        foot = tk.Frame(shell, bg=TOP_BG, pady=10, padx=14,
                        highlightthickness=1, highlightbackground=BORDER)
        foot.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(14,0))
        self._lbl_status = tk.Label(foot, text="", font=("Segoe UI",9),
                                    bg=TOP_BG, fg=DIM)
        self._lbl_status.pack(side="left", padx=14)
        self._lbl_count = tk.Label(foot, text="0/0",
                                   font=("Segoe UI",9), bg=TOP_BG, fg=DIM)
        self._lbl_count.pack(side="right", padx=14)
        self._prog = ttk.Progressbar(foot, length=160, mode="determinate",
                                     style="Studio.Horizontal.TProgressbar")
        self._prog.pack(side="right", padx=6)
        self._render_mode_toggle()
        self._refresh_language_toggle()
        self.after(0, self._update_layout_constraints)

    def _build_left(self, p):
        p.columnconfigure(0, weight=1)

        top_row = tk.Frame(p, bg=CARD)
        top_row.grid(row=0, column=0, sticky="ew")
        top_row.columnconfigure(0, weight=1)
        self._lbl_left_title = tk.Label(top_row, text=self._t("your_images"),
                                        font=("Segoe UI",12,"bold"), bg=CARD, fg=TEXT)
        self._lbl_left_title.grid(row=0, column=0, sticky="w")

        actions = tk.Frame(top_row, bg=CARD)
        actions.grid(row=1, column=0, sticky="w", pady=(10,0))
        self._btn_add = self._mkbtn(actions, self._t("add"), self._add_files, bg=CARD2, hover="#202938",
                                    pady=5, font=("Segoe UI",8,"bold"), padx=7)
        self._btn_add.pack(side="left", padx=(0,4))
        self._btn_folder = self._mkbtn(actions, self._t("folder"), self._add_folder, bg=CARD2, hover="#202938",
                                       pady=5, font=("Segoe UI",8,"bold"), padx=7)
        self._btn_folder.pack(side="left", padx=(0,4))
        self._btn_remove_file = self._mkbtn(actions, self._t("remove"), self._remove_selected_file,
                                            bg=CARD2, hover="#3A2430", pady=5, font=("Segoe UI",8,"bold"), padx=7)
        self._btn_remove_file.pack(side="left")
        self._set_button_enabled(self._btn_remove_file, False)

        self._lbl_left_sub = tk.Label(p, text=self._t("your_images_sub"),
                                      font=("Segoe UI",9), bg=CARD, fg=DIM,
                                      wraplength=230, justify="left", anchor="w")
        self._lbl_left_sub.grid(row=1, column=0, sticky="ew", pady=(10,12))

        list_card = tk.Frame(p, bg=CARD2, highlightthickness=1, highlightbackground=BORDER)
        list_card.grid(row=2, column=0, sticky="nsew")
        list_card.columnconfigure(0, weight=1)
        list_card.rowconfigure(0, weight=1)
        p.rowconfigure(2, weight=1)

        list_wrap = tk.Frame(list_card, bg=CARD2)
        list_wrap.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        list_wrap.columnconfigure(0, weight=1)
        list_wrap.rowconfigure(0, weight=1)

        self._files_canvas = tk.Canvas(list_wrap, bg=CARD2, highlightthickness=0, bd=0)
        self._files_canvas.grid(row=0, column=0, sticky="nsew")
        files_scroll = ttk.Scrollbar(list_wrap, style="Studio.Vertical.TScrollbar",
                                     orient="vertical", command=self._files_canvas.yview)
        files_scroll.grid(row=0, column=1, sticky="ns")
        self._files_canvas.configure(yscrollcommand=files_scroll.set)
        self._files_inner = tk.Frame(self._files_canvas, bg=CARD2)
        self._files_window = self._files_canvas.create_window((0, 0), window=self._files_inner, anchor="nw")
        self._files_inner.bind("<Configure>", lambda _e: self._files_canvas.configure(
            scrollregion=self._files_canvas.bbox("all")))
        self._files_canvas.bind("<Configure>", lambda e: self._files_canvas.itemconfigure(
            self._files_window, width=e.width))
        for widget in (list_card, list_wrap, self._files_canvas, self._files_inner):
            widget.bind("<Enter>", lambda _e, target=self._files_canvas: self._set_mousewheel_target(target), add="+")
            widget.bind("<Leave>", lambda _e: self._set_mousewheel_target(None), add="+")

        export_card = tk.Frame(p, bg=CARD2, highlightthickness=1, highlightbackground=BORDER)
        export_card.grid(row=3, column=0, sticky="ew", pady=(14,0))
        export_card.columnconfigure(0, weight=1)
        self._lbl_export_title = tk.Label(export_card, text=self._t("export"),
                 font=("Segoe UI",11,"bold"), bg=CARD2, fg=TEXT)
        self._lbl_export_title.grid(
                     row=0, column=0, sticky="w", padx=14, pady=(14,4))
        self._lbl_out = tk.Label(export_card, text=self._t("same_folder"),
                                 font=("Segoe UI",9), bg=CARD2, fg=DIM,
                                 wraplength=220, justify="left", anchor="w")
        self._lbl_out.grid(row=1, column=0, sticky="ew", padx=14)
        self._btn_change_folder = self._mkbtn(export_card, self._t("change_folder"), self._choose_out,
                                              bg=CARD, hover="#202938", pady=6,
                                              font=("Segoe UI",9,"bold"))
        self._btn_change_folder.grid(row=2, column=0, sticky="ew", padx=14, pady=(12,0))
        self._export_combo = ttk.Combobox(
            export_card,
            textvariable=self._export_format,
            values=[],
            state="readonly",
            style="Studio.TCombobox"
        )
        self._export_combo.grid(row=3, column=0, sticky="ew", padx=14, pady=(10,8))
        self._export_combo.bind("<<ComboboxSelected>>", self._on_export_format_change)
        self._btn_export_sidebar = self._mkbtn(export_card, self._t("export_file"), self._export_current,
                                               bg=CARD, hover="#202938", pady=10,
                                               font=("Segoe UI",10,"bold"))
        self._btn_export_sidebar.grid(row=4, column=0, sticky="ew", padx=14, pady=(0,14))
        self._btn_export_sidebar.config(state="disabled")
        self._btn_copy_sidebar = self._mkbtn(export_card, self._t("copy_image"), self._copy_current_to_clipboard,
                                             bg=CARD, hover="#202938", pady=9,
                                             font=("Segoe UI",9,"bold"))
        self._btn_copy_sidebar.grid(row=5, column=0, sticky="ew", padx=14, pady=(0,14))
        self._btn_copy_sidebar.config(state="disabled")

    def _build_right(self, p):
        top_row = tk.Frame(p, bg=CARD)
        top_row.grid(row=0, column=0, sticky="ew")
        top_row.columnconfigure(1, weight=1)
        self._lbl_preview_title = tk.Label(top_row, text=self._t("preview"),
                                           font=("Segoe UI",12,"bold"), bg=CARD, fg=TEXT)
        self._lbl_preview_title.grid(row=0, column=0, sticky="w")
        self._lbl_preview_sub = tk.Label(top_row, text=self._t("preview_sub"),
                                         font=("Segoe UI",9), bg=CARD, fg=DIM,
                                         wraplength=360, justify="left", anchor="w")
        self._lbl_preview_sub.grid(row=1, column=0, sticky="ew", pady=(4,0))

        meta = tk.Frame(top_row, bg=CARD)
        meta.grid(row=0, column=2, rowspan=2, sticky="e")
        tk.Label(meta, textvariable=self._zoom_text, font=("Segoe UI",10,"bold"),
                 bg=CARD, fg=TEXT).pack(side="left", padx=(0,16))
        tk.Label(meta, textvariable=self._resolution_text, font=("Segoe UI",9),
                 bg=CARD, fg=DIM).pack(side="left")

        mode_row = tk.Frame(p, bg=CARD)
        mode_row.grid(row=1, column=0, sticky="ew", pady=(18,12))
        self._btn_view_before = self._mkbtn(mode_row, self._t("before"),
                                            lambda: self._set_view_mode("before"),
                                            bg=CARD2, hover="#202938", pady=7,
                                            font=("Segoe UI",10,"bold"))
        self._btn_view_before.pack(side="left")
        tk.Frame(mode_row, bg=CARD, width=8).pack(side="left")
        self._btn_view_after = self._mkbtn(mode_row, self._t("after"),
                                           lambda: self._set_view_mode("after"),
                                           bg=CARD2, hover="#202938", pady=7,
                                           font=("Segoe UI",10,"bold"))
        self._btn_view_after.pack(side="left")
        tk.Frame(mode_row, bg=CARD, width=8).pack(side="left")
        self._btn_view_split = self._mkbtn(mode_row, self._t("split"),
                                           lambda: self._set_view_mode("split"),
                                           bg=CARD2, hover="#202938", pady=7,
                                           font=("Segoe UI",10,"bold"))
        self._btn_view_split.pack(side="left")
        tk.Frame(mode_row, bg=CARD, width=16).pack(side="left")
        self._btn_undo_preview = self._mkbtn(mode_row, "↩", self._undo_manual_edit,
                                             bg=CARD2, hover="#202938", pady=7,
                                             font=("Segoe UI",10,"bold"))
        self._btn_undo_preview.pack(side="left")

        zoom_bar = tk.Frame(mode_row, bg=CARD)
        zoom_bar.pack(side="right")
        self._mkbtn(zoom_bar, "-", lambda: self._change_preview_zoom(-0.2),
                    bg=CARD2, hover="#202938", pady=6,
                    font=("Segoe UI",10,"bold")).pack(side="left")
        tk.Frame(zoom_bar, bg=CARD, width=8).pack(side="left")
        self._mkbtn(zoom_bar, "+", lambda: self._change_preview_zoom(0.2),
                    bg=CARD2, hover="#202938", pady=6,
                    font=("Segoe UI",10,"bold")).pack(side="left")
        tk.Frame(zoom_bar, bg=CARD, width=8).pack(side="left")
        self._btn_fit = self._mkbtn(zoom_bar, self._t("fit"), self._fit_preview_zoom,
                                    bg=CARD2, hover="#202938", pady=6,
                                    font=("Segoe UI",10,"bold"))
        self._btn_fit.pack(side="left")

        stage = tk.Frame(p, bg=CARD, highlightthickness=1, highlightbackground=BORDER_SOFT)
        stage.grid(row=2, column=0, sticky="nsew")
        stage.columnconfigure(0, weight=0, minsize=260)
        stage.columnconfigure(1, weight=0, minsize=8)
        stage.columnconfigure(2, weight=0, minsize=260)
        stage.rowconfigure(0, weight=1)
        self._preview_stage = stage

        self._card_b = self._make_card(stage, "original")
        self._card_b.grid(row=0, column=0, sticky="nsew")
        self._splitter = tk.Frame(stage, bg=BORDER_SOFT, width=8, cursor="sb_h_double_arrow")
        self._splitter.grid(row=0, column=1, sticky="ns")
        self._splitter.bind("<ButtonPress-1>", self._start_splitter_drag)
        self._splitter.bind("<B1-Motion>", self._drag_splitter)
        self._card_a = self._make_card(stage, "removed")
        self._card_a.grid(row=0, column=2, sticky="nsew")
        stage.bind("<Configure>", self._on_preview_stage_configure, add="+")
        self._build_quick_tools(self._card_a)

        bottom_bar = tk.Frame(p, bg=CARD)
        bottom_bar.grid(row=3, column=0, sticky="ew", pady=(14,0))
        bottom_bar.columnconfigure(0, weight=1)
        self._lbl_info = tk.Label(bottom_bar, text="", font=("Segoe UI",9),
                                  bg=CARD, fg=DIM)
        self._lbl_info.grid(row=0, column=0, sticky="w")
        self._set_view_mode("split")

    def _build_controls(self, p):
        p.columnconfigure(0, weight=1)
        p.rowconfigure(1, weight=1)

        header = tk.Frame(p, bg=CARD)
        header.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0,10))
        header.columnconfigure(0, weight=1)
        self._controls_header = header
        self._controls_header_text = tk.Frame(header, bg=CARD)
        self._controls_header_text.grid(row=0, column=0, sticky="ew")

        self._lbl_controls_title = tk.Label(self._controls_header_text, text=self._t("adjustments"),
                 font=("Segoe UI",12,"bold"), bg=CARD, fg=TEXT)
        self._lbl_controls_title.grid(row=0, column=0, sticky="w")
        self._lbl_controls_sub = tk.Label(self._controls_header_text, text=self._t("adjustments_sub"),
                 font=("Segoe UI",9), bg=CARD, fg=DIM,
                 wraplength=212, justify="left", anchor="w")
        self._lbl_controls_sub.grid(row=1, column=0, sticky="ew", pady=(6,0), padx=(4,0))

        self._btn_controls_toggle = self._mkbtn(
            header, "<<", self._toggle_controls_panel,
            bg=CARD2, hover="#202938", pady=5, font=("Segoe UI",9,"bold"), padx=9
        )
        self._btn_controls_toggle.grid(row=0, column=1, sticky="ne", padx=(8,0))

        content = tk.Frame(p, bg=CARD)
        content.grid(row=1, column=0, columnspan=2, sticky="nsew")
        content.columnconfigure(0, weight=1)
        content.rowconfigure(0, weight=1)
        self._controls_content = content

        canvas = tk.Canvas(content, bg=CARD, highlightthickness=0, bd=0)
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar = ttk.Scrollbar(
            content, style="Studio.Vertical.TScrollbar", orient="vertical", command=canvas.yview
        )
        scrollbar.grid(row=0, column=1, sticky="ns", padx=(10,0))
        canvas.configure(yscrollcommand=scrollbar.set)

        inner = tk.Frame(canvas, bg=CARD)
        inner.columnconfigure(0, weight=1)
        self._controls_canvas = canvas
        self._controls_inner = inner
        self._controls_window = canvas.create_window((0, 0), window=inner, anchor="nw")
        self._controls_scrollbar = scrollbar
        inner.bind("<Configure>", lambda _e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(self._controls_window, width=max(10, e.width)))
        canvas.bind("<Enter>", lambda _e: self._set_mousewheel_target(canvas))
        canvas.bind("<Leave>", lambda _e: self._set_mousewheel_target(None))
        inner.bind("<Enter>", lambda _e: self._set_mousewheel_target(canvas))
        inner.bind("<Leave>", lambda _e: self._set_mousewheel_target(None))

        self._white_slider_card = self._build_compact_slider(inner, "white_threshold", self._thr_main, 180, 255, 0)
        self._color_card = self._build_color_detect_card(inner, 1)
        self._edge_slider_card = self._build_compact_slider(inner, "edge_cleanup", self._erode_ret, 0, 8, 2)
        self._sticker_card = self._build_sticker_controls(inner, 3)
        self._resize_card = self._build_resize_controls(inner, 4)
        self._manual_card = self._build_manual_controls(inner, 5)

        self._btn_run = self._make_glow_button(inner, self._t("remove_bg"), self._start)
        self._btn_run.grid(row=6, column=0, sticky="ew", pady=(22,12))

        self._btn_refine = self._mkbtn(
            inner, self._t("refine_edges"), self._apply_retouch,
            bg=CARD2, hover="#202938", pady=11, font=("Segoe UI",11,"bold")
        )
        self._btn_refine.grid(row=7, column=0, sticky="ew", pady=(0,10))

        self._btn_export = self._mkbtn(
            inner, self._t("export_file"), self._export_current,
            bg=CARD2, hover="#202938", pady=11, font=("Segoe UI",11,"bold")
        )
        self._btn_export.grid(row=8, column=0, sticky="ew")
        self._btn_copy = self._mkbtn(
            inner, self._t("copy_image"), self._copy_current_to_clipboard,
            bg=CARD2, hover="#202938", pady=11, font=("Segoe UI",11,"bold")
        )
        self._btn_copy.grid(row=9, column=0, sticky="ew", pady=(10,0))
        self._btn_save = self._btn_export

        self._lbl_simple_note = tk.Label(
            inner,
            text=self._t("simple_note"),
            font=("Segoe UI",9), bg=CARD, fg=MUTED, justify="left", wraplength=212
        )
        self._lbl_simple_note.grid(row=10, column=0, sticky="ew", pady=(18,0), padx=(4,0))
        tk.Frame(inner, bg=CARD, height=14).grid(row=11, column=0, sticky="ew")

        self._set_secondary_buttons_enabled(False)
        self._apply_controls_panel_layout()

    def _build_compact_slider(self, parent, label_key, var, from_, to, row):
        wrap = tk.Frame(parent, bg=CARD2, padx=14, pady=12,
                        highlightthickness=1, highlightbackground=BORDER)
        wrap.grid(row=row, column=0, sticky="ew", pady=(0,12))
        wrap.columnconfigure(0, weight=1)

        expanded = tk.BooleanVar(value=(label_key == "white_threshold"))
        wrap._expanded_var = expanded
        wrap._body = tk.Frame(wrap, bg=CARD2)
        wrap._body.columnconfigure(0, weight=1)

        top = tk.Frame(wrap, bg=CARD2, cursor="hand2")
        top.grid(row=0, column=0, sticky="ew")
        top.columnconfigure(0, weight=1)
        lbl = tk.Label(top, text=self._t(label_key), font=("Segoe UI",10), bg=CARD2, fg=SOFT_TEXT, cursor="hand2")
        lbl.pack(side="left")
        tk.Label(top, textvariable=var, font=("Segoe UI",10,"bold"), bg=CARD2, fg=TEXT).pack(side="right")
        toggle = tk.Label(top, text="−" if expanded.get() else "+", font=("Segoe UI",11,"bold"),
                          bg=CARD2, fg=DIM, cursor="hand2")
        toggle.pack(side="right", padx=(0,10))
        wrap._toggle_label = toggle
        self._slider_label_refs[label_key] = lbl

        tk.Scale(wrap._body, variable=var, from_=from_, to=to,
                 orient="horizontal", bg=CARD2, fg=TEXT,
                 highlightthickness=0, troughcolor="#243041",
                 activebackground=ACCENT, sliderrelief="flat", bd=0,
                 font=("Segoe UI",8), showvalue=0).grid(row=0, column=0, sticky="ew", pady=(12,2))
        wrap._body.grid(row=1, column=0, sticky="ew")

        def _toggle(_event=None, target=wrap):
            self._toggle_expandable_card(target)

        for widget in (top, lbl, toggle):
            widget.bind("<Button-1>", _toggle, add="+")
        self._apply_expandable_card_state(wrap)
        return wrap

    def _build_color_detect_card(self, parent, row):
        """Card com amostras de cores detectadas do fundo + controles de filtro de cor."""
        card = tk.Frame(parent, bg=CARD2, padx=14, pady=10,
                        highlightthickness=1, highlightbackground=BORDER)
        card.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        card.columnconfigure(0, weight=1)

        # ── Cabeçalho ──────────────────────────────────────────────────
        header = tk.Frame(card, bg=CARD2)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)

        self._lbl_color_title = tk.Label(
            header, text=self._t("bg_colors_title"),
            font=("Segoe UI", 10), bg=CARD2, fg=SOFT_TEXT
        )
        self._lbl_color_title.pack(side="left")

        self._btn_refresh_colors = self._mkbtn(
            header, "⟳", self._refresh_color_swatches,
            bg=CARD2, hover="#202938", pady=1, padx=6, font=("Segoe UI", 11)
        )
        self._btn_refresh_colors.pack(side="right")

        self._lbl_color_sub = tk.Label(
            card, text=self._t("bg_colors_sub"),
            font=("Segoe UI", 8), bg=CARD2, fg=MUTED,
            justify="left", wraplength=180, anchor="w"
        )
        self._lbl_color_sub.grid(row=1, column=0, sticky="ew", pady=(4, 0))

        # ── Swatches ───────────────────────────────────────────────────
        swatch_row = tk.Frame(card, bg=CARD2)
        swatch_row.grid(row=2, column=0, sticky="w", pady=(10, 0))

        self._color_swatches = []
        for i in range(5):
            sw = tk.Frame(swatch_row, width=30, height=30, bg="#1a2233",
                          highlightthickness=2, highlightbackground="#333344",
                          cursor="hand2")
            sw.pack(side="left", padx=(0, 6))
            sw.pack_propagate(False)
            sw._active = False    # True = this color WILL be removed
            sw._color  = None     # (r, g, b) or None if empty slot
            sw._index  = i
            sw.bind("<Button-1>", lambda _e, s=sw: self._toggle_color_swatch(s))
            self._color_swatches.append(sw)

        # ── Corpo avançado (oculto em Modo Simples) ────────────────────
        body = tk.Frame(card, bg=CARD2)
        body.columnconfigure(1, weight=1)
        card._color_body = body

        # Tolerância
        self._lbl_color_tolerance = tk.Label(body, text=self._t("color_tolerance"),
                                              font=("Segoe UI", 9), bg=CARD2, fg=SOFT_TEXT)
        self._lbl_color_tolerance.grid(row=0, column=0, sticky="w", pady=(10, 0))
        tk.Label(body, textvariable=self._color_key_tol,
                 font=("Segoe UI", 9, "bold"), bg=CARD2, fg=TEXT).grid(
            row=0, column=2, sticky="e", padx=(6, 0), pady=(10, 0))
        tk.Scale(body, variable=self._color_key_tol, from_=10, to=100,
                 orient="horizontal", bg=CARD2, fg=TEXT,
                 highlightthickness=0, troughcolor="#243041",
                 activebackground=ACCENT, sliderrelief="flat", bd=0,
                 showvalue=0).grid(row=0, column=1, sticky="ew", padx=(8, 8), pady=(10, 0))

        # Supressão de spill
        spill_row = tk.Frame(body, bg=CARD2)
        spill_row.grid(row=1, column=0, columnspan=3, sticky="ew", pady=(6, 0))
        self._lbl_spill = tk.Label(spill_row, text=self._t("spill_suppress"),
                                   font=("Segoe UI", 9), bg=CARD2, fg=SOFT_TEXT)
        self._lbl_spill.pack(side="left")
        tk.Checkbutton(spill_row, variable=self._spill_suppress,
                       bg=CARD2, fg=TEXT, selectcolor=CARD2,
                       activebackground=CARD2, activeforeground=TEXT,
                       highlightthickness=0, bd=0).pack(side="right")

        # Botões re-aplicar + desfazer (lado a lado)
        btn_row = tk.Frame(body, bg=CARD2)
        btn_row.grid(row=2, column=0, columnspan=3, sticky="ew", pady=(10, 0))
        btn_row.columnconfigure(0, weight=1)

        self._btn_reapply_colors = self._mkbtn(
            btn_row, self._t("reapply_colors"), self._apply_color_key_pass,
            bg=CARD2, hover="#202938", pady=8, font=("Segoe UI", 10, "bold")
        )
        self._btn_reapply_colors.grid(row=0, column=0, sticky="ew")

        self._btn_undo_color = self._mkbtn(
            btn_row, "↩", self._undo_manual_edit,
            bg=CARD2, hover="#202938", pady=8, padx=10, font=("Segoe UI", 11)
        )
        self._btn_undo_color.grid(row=0, column=1, sticky="ew", padx=(6, 0))

        body.grid(row=3, column=0, sticky="ew")
        return card

    def _toggle_color_swatch(self, swatch):
        """Alterna o estado ativo de uma amostra de cor (ativa = será removida)."""
        if swatch._color is None:
            return
        swatch._active = not swatch._active
        if swatch._active:
            swatch.config(highlightbackground=ACCENT, highlightthickness=2)
        else:
            # Dim border when excluded from removal
            swatch.config(highlightbackground="#444455", highlightthickness=2)
            # Overlay dark tint to signal "excluded"
            r, g, b = swatch._color
            # Blend towards dark to signal disabled
            dr = int(r * 0.35)
            dg = int(g * 0.35)
            db = int(b * 0.35)
            swatch.config(bg=f"#{dr:02x}{dg:02x}{db:02x}")
        # Restore full color when active
        if swatch._active and swatch._color:
            r, g, b = swatch._color
            swatch.config(bg=f"#{r:02x}{g:02x}{b:02x}")

    def _update_color_swatches(self, img: "Image.Image"):
        """Detecta as cores do fundo, sugere limiar de branco e atualiza as amostras na UI."""
        if not hasattr(self, "_color_swatches"):
            return
        try:
            colors = detectar_paleta_fundo(img, n_colors=5)
        except Exception:
            colors = []
        self._detected_colors = colors

        # Auto-sugere o limiar de branco ideal para este fundo
        try:
            suggested_thr = sugerir_limiar_branco(img)
            self._thr_main.set(suggested_thr)
        except Exception:
            pass

        # Auto-ajusta tolerância do filtro de cor com base na saturação do fundo.
        # Fundo colorido saturado (amarelo, laranja, verde…) gera franjas mais distantes
        # da cor pura detectada, então precisa de tolerância maior para a erosão funcionar.
        try:
            bg_rgb = estimate_background_color(img)
            bg_sat = float(np.max(bg_rgb) - np.min(bg_rgb))
            bg_bri = float(np.mean(bg_rgb))
            if bg_sat > 80:                          # fundo colorido saturado
                self._color_key_tol.set(50)
            elif bg_sat > 40:                        # fundo levemente saturado
                self._color_key_tol.set(55)
            elif bg_bri > 210:                       # fundo muito claro/branco
                self._color_key_tol.set(45)
            else:                                    # fundo escuro ou neutro
                self._color_key_tol.set(30)
        except Exception:
            pass

        for i, sw in enumerate(self._color_swatches):
            if i < len(colors):
                r, g, b = colors[i]
                sw._color = (r, g, b)
                sw._active = True
                sw.config(bg=f"#{r:02x}{g:02x}{b:02x}",
                          highlightbackground=ACCENT,
                          highlightthickness=2, cursor="hand2")
            else:
                sw._color = None
                sw._active = False
                sw.config(bg="#1a2233", highlightbackground="#333344",
                          highlightthickness=2, cursor="arrow")

    def _refresh_color_swatches(self):
        """Re-detecta cores do fundo a partir da imagem selecionada atual."""
        if self._sel is None or self._sel >= len(self._files):
            return
        try:
            img = Image.open(self._files[self._sel])
            self._update_color_swatches(img)
        except Exception:
            pass

    def _get_active_removal_colors(self) -> list:
        """Retorna lista de (r,g,b) para cores ativas (marcadas para remoção)."""
        if not hasattr(self, "_color_swatches"):
            return []
        return [sw._color for sw in self._color_swatches
                if sw._active and sw._color is not None]

    def _apply_color_key_pass(self):
        """Re-aplica apenas o filtro de cores ao resultado existente (sem reprocessar)."""
        if self._sel is None or self._sel >= len(self._files):
            return
        path = self._files[self._sel]
        base = self._retouched.get(path) or self._results.get(path)
        if base is None:
            return
        active = self._get_active_removal_colors()
        if not active:
            return
        try:
            src = Image.open(path).convert("RGB")
            result = aplicar_color_key(
                base, src, active,
                tolerance=self._color_key_tol.get(),
                suppress_spill=self._spill_suppress.get()
            )
            # Salva estado ANTES de aplicar no histórico (permite Desfazer)
            if path not in self._manual_history:
                self._reset_history(path, base)
            else:
                self._push_history_snapshot(path, base)

            self._results[path] = result
            self._retouched.pop(path, None)
            # Salva novo estado no histórico
            self._push_history_snapshot(path, result)

            self.after(0, lambda: (
                self._set_card(self._card_a, result),
                self._set_status(self._t("color_filter_done"), SUCCESS),
                self._set_secondary_buttons_enabled(True),
            ))
        except Exception as e:
            print(f"Color key pass error: {e}")

    def _build_sticker_controls(self, parent, row):
        wrap = tk.Frame(parent, bg=CARD2, padx=14, pady=10,
                        highlightthickness=1, highlightbackground=BORDER)
        wrap.grid(row=row, column=0, sticky="ew", pady=(0, 12))
        wrap.columnconfigure(0, weight=1)

        header = tk.Frame(wrap, bg=CARD2)
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        header.columnconfigure(0, weight=1)

        self._lbl_sticker_title = tk.Label(
            header, text=self._t("sticker_mode"),
            font=("Segoe UI", 10, "bold"), bg=CARD2, fg=SOFT_TEXT
        )
        self._lbl_sticker_title.pack(side="left")

        self._chk_sticker = tk.Checkbutton(
            header,
            variable=self._sticker_mode,
            bg=CARD2, fg=TEXT,
            selectcolor=CARD2,
            activebackground=CARD2,
            activeforeground=TEXT,
            highlightthickness=0, bd=0,
        )
        self._chk_sticker.pack(side="right")

        self._lbl_sticker_sub = tk.Label(
            wrap, text=self._t("sticker_mode_sub"),
            font=("Segoe UI", 8), bg=CARD2, fg=MUTED,
            justify="left", wraplength=172, anchor="w"
        )
        self._lbl_sticker_sub.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(6, 0))

        return wrap

    def _build_resize_controls(self, parent, row):
        card = tk.Frame(parent, bg=CARD2, padx=14, pady=12,
                        highlightthickness=1, highlightbackground=BORDER)
        card.grid(row=row, column=0, sticky="ew", pady=(0,12))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        expanded = tk.BooleanVar(value=False)
        card._expanded_var = expanded
        card._body = tk.Frame(card, bg=CARD2)
        card._body.columnconfigure(0, weight=1)
        card._body.columnconfigure(1, weight=1)

        header = tk.Frame(card, bg=CARD2, cursor="hand2")
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self._lbl_resize_title = tk.Label(
            header, text=self._t("output_size"), font=("Segoe UI",10), bg=CARD2, fg=SOFT_TEXT, cursor="hand2"
        )
        self._lbl_resize_title.pack(side="left")
        card._toggle_label = tk.Label(header, text="+", font=("Segoe UI",11,"bold"),
                                      bg=CARD2, fg=DIM, cursor="hand2")
        card._toggle_label.pack(side="right")
        self._lbl_resize_sub = tk.Label(
            card._body, text=self._t("output_size_sub"), font=("Segoe UI",8),
            bg=CARD2, fg=MUTED, justify="left", wraplength=160
        )
        self._lbl_resize_sub.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(4,10))

        self._resize_enable_chk = tk.Checkbutton(
            card,
            text=self._t("resize_enable"),
            variable=self._resize_enabled,
            command=self._on_resize_toggle,
            bg=CARD2,
            fg=TEXT,
            selectcolor=CARD2,
            activebackground=CARD2,
            activeforeground=TEXT,
            highlightthickness=0,
            bd=0,
            font=("Segoe UI",9, "bold"),
            anchor="w",
            justify="left",
            wraplength=160,
        )
        self._resize_enable_chk.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,10), in_=card._body)

        self._lbl_resize_orig = tk.Label(
            card, text=self._t("original_select"), font=("Segoe UI",8),
            bg=CARD2, fg=DIM, justify="left", wraplength=186
        )
        self._lbl_resize_orig.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(0,10), in_=card._body)

        self._lbl_resize_width = tk.Label(card, text=self._t("width_label"), font=("Segoe UI",8),
                                          bg=CARD2, fg=MUTED)
        self._lbl_resize_width.grid(row=3, column=0, sticky="w", in_=card._body)
        self._lbl_resize_height = tk.Label(card, text=self._t("height_label"), font=("Segoe UI",8),
                                           bg=CARD2, fg=MUTED)
        self._lbl_resize_height.grid(row=3, column=1, sticky="w", padx=(8,0), in_=card._body)

        self._entry_resize_width = tk.Entry(
            card, textvariable=self._resize_width, justify="center", relief="flat", bd=0,
            bg="#121C2A", fg=TEXT, insertbackground=TEXT, disabledbackground="#121C2A",
            disabledforeground=MUTED, highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, font=("Segoe UI",10)
        )
        self._entry_resize_width.grid(row=4, column=0, sticky="ew", in_=card._body)

        right_col = tk.Frame(card._body, bg=CARD2)
        right_col.grid(row=4, column=1, sticky="ew", padx=(8,0))
        right_col.columnconfigure(0, weight=1)

        self._entry_resize_height = tk.Entry(
            right_col, textvariable=self._resize_height, justify="center", relief="flat", bd=0,
            bg="#121C2A", fg=TEXT, insertbackground=TEXT, disabledbackground="#121C2A",
            disabledforeground=MUTED, highlightthickness=1, highlightbackground=BORDER,
            highlightcolor=ACCENT, font=("Segoe UI",10)
        )
        self._entry_resize_height.grid(row=0, column=0, sticky="ew")

        self._btn_resize_lock = self._mkbtn(
            card, "🔒", self._toggle_resize_lock, bg=CARD, hover="#202938",
            pady=5, font=("Segoe UI",9,"bold"), padx=8
        )
        self._btn_resize_lock.grid(row=5, column=0, columnspan=2, sticky="w", pady=(10,0), in_=card._body)
        self._lbl_resize_lock = tk.Label(
            card, text=self._t("lock_ratio"), font=("Segoe UI",8),
            bg=CARD2, fg=MUTED
        )
        self._lbl_resize_lock.grid(row=5, column=0, columnspan=2, sticky="w", padx=(46,0), pady=(10,0), in_=card._body)

        # Separador
        tk.Frame(card._body, bg=BORDER, height=1).grid(row=6, column=0, columnspan=2, sticky="ew", pady=(14,0))

        # Botão exportar original redimensionado
        self._btn_export_resized_orig = self._mkbtn(
            card._body, self._t("export_resized_original"), self._export_original_resized,
            bg=CARD, hover="#202938", pady=8, font=("Segoe UI", 9, "bold")
        )
        self._btn_export_resized_orig.grid(row=7, column=0, columnspan=2, sticky="ew", pady=(8, 0))

        card._body.grid(row=1, column=0, columnspan=2, sticky="ew")
        for widget in (header, self._lbl_resize_title, card._toggle_label):
            widget.bind("<Button-1>", lambda _e, target=card: self._toggle_expandable_card(target), add="+")
        self._apply_expandable_card_state(card)
        self._update_resize_controls_state()
        return card

    def _build_manual_controls(self, parent, row):
        card = tk.Frame(parent, bg=CARD2, padx=14, pady=12,
                        highlightthickness=1, highlightbackground=BORDER)
        card.grid(row=row, column=0, sticky="ew", pady=(0,12))
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        expanded = tk.BooleanVar(value=False)
        card._expanded_var = expanded
        card._body = tk.Frame(card, bg=CARD2)
        card._body.columnconfigure(0, weight=1)
        card._body.columnconfigure(1, weight=1)

        header = tk.Frame(card, bg=CARD2, cursor="hand2")
        header.grid(row=0, column=0, columnspan=2, sticky="ew")
        self._lbl_manual_title = tk.Label(header, text=self._t("manual_tools"),
                                          font=("Segoe UI",10), bg=CARD2, fg=SOFT_TEXT, cursor="hand2")
        self._lbl_manual_title.pack(side="left")
        card._toggle_label = tk.Label(header, text="+", font=("Segoe UI",11,"bold"),
                                      bg=CARD2, fg=DIM, cursor="hand2")
        card._toggle_label.pack(side="right")
        self._lbl_manual_sub = tk.Label(card._body, text=self._t("manual_tools_sub"),
                                        font=("Segoe UI",8), bg=CARD2, fg=MUTED,
                                        justify="left", wraplength=160)
        self._lbl_manual_sub.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(4,10))

        self._process_selected_chk = tk.Checkbutton(
            card,
            text=self._t("process_selected_only"),
            variable=self._process_selected_only,
            bg=CARD2,
            fg=TEXT,
            selectcolor=CARD2,
            activebackground=CARD2,
            activeforeground=TEXT,
            highlightthickness=0,
            bd=0,
            font=("Segoe UI",9, "bold"),
            anchor="w",
            justify="left",
            wraplength=160,
        )
        self._process_selected_chk.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,10), in_=card._body)

        self._hair_protect_chk = tk.Checkbutton(
            card,
            text=self._t("hair_protect"),
            variable=self._hair_protect,
            bg=CARD2,
            fg=TEXT,
            selectcolor=CARD2,
            activebackground=CARD2,
            activeforeground=TEXT,
            highlightthickness=0,
            bd=0,
            font=("Segoe UI",9, "bold"),
            anchor="w",
        )
        self._hair_protect_chk.grid(row=2, column=0, columnspan=2, sticky="ew", in_=card._body)
        self._lbl_hair_sub = tk.Label(card, text=self._t("hair_protect_sub"),
                                      font=("Segoe UI",8), bg=CARD2, fg=DIM,
                                      justify="left", wraplength=160)
        self._lbl_hair_sub.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(4,10), in_=card._body)

        self._lbl_manual_tool = tk.Label(card, text=self._t("manual_tool"), font=("Segoe UI",8),
                                         bg=CARD2, fg=MUTED)
        self._lbl_manual_tool.grid(row=4, column=0, sticky="w", in_=card._body)
        self._lbl_brush_shape = tk.Label(card, text=self._t("brush_shape"), font=("Segoe UI",8),
                                         bg=CARD2, fg=MUTED)
        self._lbl_brush_shape.grid(row=4, column=1, sticky="w", padx=(8,0), in_=card._body)

        self._manual_tool_combo = ttk.Combobox(card, state="readonly", style="Studio.TCombobox")
        self._manual_tool_combo.grid(row=5, column=0, sticky="ew", in_=card._body)
        self._manual_tool_combo.bind("<<ComboboxSelected>>", self._on_manual_tool_change)
        self._brush_shape_combo = ttk.Combobox(card, state="readonly", style="Studio.TCombobox")
        self._brush_shape_combo.grid(row=5, column=1, sticky="ew", padx=(8,0), in_=card._body)
        self._brush_shape_combo.bind("<<ComboboxSelected>>", self._on_brush_shape_change)

        self._lbl_brush_size = tk.Label(card, text=self._t("brush_size"), font=("Segoe UI",8),
                                        bg=CARD2, fg=MUTED)
        self._lbl_brush_size.grid(row=6, column=0, sticky="w", pady=(10,0), in_=card._body)
        tk.Label(card, textvariable=self._brush_size, font=("Segoe UI",9,"bold"),
                 bg=CARD2, fg=TEXT).grid(row=6, column=1, sticky="e", pady=(10,0), in_=card._body)
        tk.Scale(card._body, variable=self._brush_size, from_=2, to=80,
                 orient="horizontal", bg=CARD2, fg=TEXT,
                 highlightthickness=0, troughcolor="#243041",
                 activebackground=ACCENT, sliderrelief="flat", bd=0,
                 font=("Segoe UI",8), showvalue=0).grid(row=7, column=0, columnspan=2, sticky="ew", pady=(8,2))

        history_row = tk.Frame(card._body, bg=CARD2)
        history_row.grid(row=8, column=0, columnspan=2, sticky="ew", pady=(8,2))
        self._btn_undo = self._mkbtn(history_row, "Undo", self._undo_manual_edit,
                                     bg=CARD, hover="#202938", pady=4, font=("Segoe UI",8,"bold"), padx=8)
        self._btn_undo.pack(side="left")
        tk.Frame(history_row, bg=CARD2, width=8).pack(side="left")
        self._btn_redo = self._mkbtn(history_row, "Redo", self._redo_manual_edit,
                                     bg=CARD, hover="#202938", pady=4, font=("Segoe UI",8,"bold"), padx=8)
        self._btn_redo.pack(side="left")

        self._lbl_manual_tip = tk.Label(card, text=self._t("manual_tip"), font=("Segoe UI",8),
                                        bg=CARD2, fg=DIM, justify="left", wraplength=160)
        self._lbl_manual_tip.grid(row=9, column=0, columnspan=2, sticky="ew", pady=(8,0), in_=card._body)

        card._body.grid(row=1, column=0, columnspan=2, sticky="ew")
        for widget in (header, self._lbl_manual_title, card._toggle_label):
            widget.bind("<Button-1>", lambda _e, target=card: self._toggle_expandable_card(target), add="+")
        self._apply_expandable_card_state(card)
        self._sync_manual_tool_combo()
        self._sync_brush_shape_combo()
        self._refresh_history_buttons()
        return card

    def _build_quick_tools(self, card):
        wrap = tk.Frame(card, bg="", bd=0, highlightthickness=0)
        wrap.place(relx=1.0, rely=1.0, x=-14, y=-16, anchor="se")
        self._quick_tools_wrap = wrap

        menu = tk.Frame(wrap, bg=CARD2, padx=8, pady=8,
                        highlightthickness=1, highlightbackground=BORDER_SOFT)
        self._quick_tools_menu = menu

        title = tk.Label(menu, text=self._t("quick_tools"), bg=CARD2, fg=SOFT_TEXT,
                         font=("Segoe UI",8,"bold"))
        title.grid(row=0, column=0, columnspan=4, sticky="w", pady=(0,6))
        self._quick_tools_title = title

        self._btn_quick_move = self._mkbtn(menu, "Move", self._toggle_preview_nav_mode,
                                           bg=CARD, hover="#202938", pady=4, font=("Segoe UI",8,"bold"), padx=8)
        self._btn_quick_move.grid(row=1, column=0, sticky="ew")
        self._btn_quick_restore = self._mkbtn(menu, "Restore", lambda: self._set_manual_tool("restore"),
                                              bg=CARD, hover="#202938", pady=4, font=("Segoe UI",8,"bold"), padx=8)
        self._btn_quick_restore.grid(row=1, column=1, sticky="ew", padx=(6,0))
        self._btn_quick_cut = self._mkbtn(menu, "Cut", lambda: self._set_manual_tool("cut"),
                                          bg=CARD, hover="#202938", pady=4, font=("Segoe UI",8,"bold"), padx=8)
        self._btn_quick_cut.grid(row=1, column=2, sticky="ew", padx=(6,0))
        self._btn_quick_off = self._mkbtn(menu, "Off", lambda: self._set_manual_tool("none"),
                                          bg=CARD, hover="#202938", pady=4, font=("Segoe UI",8,"bold"), padx=8)
        self._btn_quick_off.grid(row=1, column=3, sticky="ew", padx=(6,0))

        self._btn_shape_round = self._mkbtn(menu, "O", lambda: self._set_brush_shape("round"),
                                            bg=CARD, hover="#202938", pady=3, font=("Segoe UI",8,"bold"), padx=7)
        self._btn_shape_round.grid(row=2, column=0, sticky="ew", pady=(6,0))
        self._btn_shape_square = self._mkbtn(menu, "[]", lambda: self._set_brush_shape("square"),
                                             bg=CARD, hover="#202938", pady=3, font=("Segoe UI",8,"bold"), padx=7)
        self._btn_shape_square.grid(row=2, column=1, sticky="ew", padx=(6,0), pady=(6,0))
        self._btn_shape_triangle = self._mkbtn(menu, "/\\", lambda: self._set_brush_shape("triangle"),
                                               bg=CARD, hover="#202938", pady=3, font=("Segoe UI",8,"bold"), padx=7)
        self._btn_shape_triangle.grid(row=2, column=2, sticky="ew", padx=(6,0), pady=(6,0))
        self._btn_shape_pencil = self._mkbtn(menu, "..", lambda: self._set_brush_shape("pencil"),
                                             bg=CARD, hover="#202938", pady=3, font=("Segoe UI",8,"bold"), padx=7)
        self._btn_shape_pencil.grid(row=2, column=3, sticky="ew", padx=(6,0), pady=(6,0))

        self._btn_quick_undo = self._mkbtn(menu, "Undo", self._undo_manual_edit,
                                           bg=CARD, hover="#202938", pady=4, font=("Segoe UI",8,"bold"), padx=8)
        self._btn_quick_undo.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(6,0))
        self._btn_quick_redo = self._mkbtn(menu, "Redo", self._redo_manual_edit,
                                           bg=CARD, hover="#202938", pady=4, font=("Segoe UI",8,"bold"), padx=8)
        self._btn_quick_redo.grid(row=3, column=2, columnspan=2, sticky="ew", padx=(6,0), pady=(6,0))

        self._btn_quick_launcher = self._mkbtn(
            wrap, self._t("quick_tools_open"), self._toggle_quick_tools,
            bg="#1E2A3B", hover="#26384E", pady=6, font=("Segoe UI",9,"bold"), padx=10
        )
        self._btn_quick_launcher.pack(anchor="e")
        self._apply_quick_tools_layout()

    def _set_view_mode(self, mode: str):
        self._view_mode.set(mode)
        if mode == "before":
            self._card_a.grid_remove()
            if hasattr(self, "_splitter"):
                self._splitter.grid_remove()
            self._card_b.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=0)
        elif mode == "after":
            self._card_b.grid_remove()
            if hasattr(self, "_splitter"):
                self._splitter.grid_remove()
            self._card_a.grid(row=0, column=0, columnspan=3, sticky="nsew", padx=0)
        else:
            self._card_b.grid(row=0, column=0, columnspan=1, sticky="nsew", padx=0)
            if hasattr(self, "_splitter"):
                self._splitter.grid(row=0, column=1, sticky="ns")
            self._card_a.grid(row=0, column=2, columnspan=1, sticky="nsew", padx=0)
            self._apply_split_ratio()

        for card in (self._card_b, self._card_a):
            if card and getattr(card, "_pil", None):
                card._offset_x = 0
                card._offset_y = 0
                card._pan_anchor = None

        self._sync_view_buttons()
        self._schedule_preview_redraw(immediate=True)

    def _start_splitter_drag(self, _event):
        self._splitter_dragging = True

    def _drag_splitter(self, event):
        if not hasattr(self, "_preview_stage"):
            return
        stage = self._preview_stage
        total = stage.winfo_width()
        if total <= 40:
            return
        local_x = event.x_root - stage.winfo_rootx()
        handle = 8
        usable = max(240, total - handle)
        min_left = 220
        max_left = max(min_left, usable - 220)
        left = max(min_left, min(int(local_x), max_left))
        self._split_ratio = left / max(usable, 1)
        self._apply_split_ratio()
        self._schedule_preview_redraw(immediate=True)

    def _on_preview_stage_configure(self, _event=None):
        self._apply_split_ratio()

    def _apply_split_ratio(self):
        if not hasattr(self, "_preview_stage") or self._view_mode.get() != "split":
            return
        total = self._preview_stage.winfo_width()
        if total <= 40:
            return
        handle = 8
        usable = max(240, total - handle)
        left = int(usable * self._split_ratio)
        left = max(220, min(left, max(220, usable - 220)))
        right = max(220, usable - left)
        self._preview_stage.columnconfigure(0, minsize=left)
        self._preview_stage.columnconfigure(2, minsize=right)

    def _sync_view_buttons(self):
        mapping = {
            "before": self._btn_view_before,
            "after": self._btn_view_after,
            "split": self._btn_view_split,
        }
        for name, btn in mapping.items():
            active = self._view_mode.get() == name
            btn.config(bg="#203149" if active else CARD2,
                       fg=TEXT if active else SOFT_TEXT)

    def _refresh_file_gallery(self):
        if not hasattr(self, "_files_inner"):
            return

        for child in self._files_inner.winfo_children():
            child.destroy()
        self._file_row_refs.clear()

        if not self._files:
            empty = tk.Label(self._files_inner, text=self._t("no_images_yet"),
                             font=("Segoe UI",10), bg=CARD2, fg=DIM,
                             justify="center", pady=26)
            empty.pack(fill="x")
            return

        for idx, path in enumerate(self._files):
            self._create_file_row(idx, path)

    def _create_file_row(self, idx: int, path: str):
        row = tk.Frame(self._files_inner, bg=CARD2, padx=8, pady=8,
                       highlightthickness=1, highlightbackground=BORDER)
        row.pack(fill="x", pady=(0,8))
        row.columnconfigure(1, weight=1)

        thumb = tk.Label(row, bg=CARD2)
        thumb.grid(row=0, column=0, rowspan=2, sticky="nw")
        thumb_img = self._make_file_thumbnail(path)
        thumb.config(image=thumb_img)
        thumb.image = thumb_img

        name = tk.Label(row, text=self._truncate_label_text(Path(path).name, 18), font=("Segoe UI",10,"bold"),
                        bg=CARD2, fg=TEXT, anchor="w")
        name.grid(row=0, column=1, sticky="ew", padx=(10,0))

        status = tk.Label(row, text=self._file_status_text(path), font=("Segoe UI",8),
                          bg=CARD2, fg=DIM, anchor="w")
        status.grid(row=1, column=1, sticky="ew", padx=(10,0), pady=(3,0))

        for widget in (row, thumb, name, status):
            widget.bind("<Button-1>", lambda _e, i=idx: self._select_index(i))
            widget.bind("<Enter>", lambda _e, p=path: self._set_file_hover(p, True))
            widget.bind("<Leave>", lambda _e, p=path: self._set_file_hover(p, False))
            widget.bind("<Enter>", lambda _e, target=self._files_canvas: self._set_mousewheel_target(target), add="+")

    def _truncate_label_text(self, text: str, limit: int = 18) -> str:
        text = str(text)
        if len(text) <= limit:
            return text
        return text[: max(3, limit - 3)] + "..."

        self._file_row_refs[path] = {"row": row, "status": status, "name": name}
        self._style_file_row(path)

    def _make_file_thumbnail(self, path: str):
        cached = self._file_thumb_cache.get(path)
        if cached is not None:
            return cached

        try:
            img = Image.open(path).convert("RGBA")
            img.thumbnail((42, 42))
            tile = Image.new("RGBA", (48, 48), (22, 27, 35, 255))
            x = (48 - img.width) // 2
            y = (48 - img.height) // 2
            tile.alpha_composite(img, (x, y))
        except Exception:
            tile = Image.new("RGBA", (48, 48), (22, 27, 35, 255))

        tkimg = ImageTk.PhotoImage(tile)
        self._file_thumb_cache[path] = tkimg
        return tkimg

    def _file_status_text(self, path: str) -> str:
        if path in self._retouched:
            return self._t("refined")
        if path in self._results:
            return self._t("processed")
        if path in self._failed_files:
            return self._t("needs_attention")
        return self._t("ready")

    def _style_file_row(self, path: str):
        refs = self._file_row_refs.get(path)
        if not refs:
            return

        active = self._sel is not None and self._files[self._sel] == path
        hovered = self._hover_file_path == path
        row = refs["row"]
        name = refs["name"]
        status = refs["status"]

        if active:
            bg = "#192436"
            row.config(bg=bg, highlightbackground=ACCENT)
            name.config(bg=bg, fg=TEXT)
            status.config(bg=bg, fg=ACCENT_CYAN)
        elif hovered:
            bg = "#1A2331"
            row.config(bg=bg, highlightbackground=BORDER_SOFT)
            name.config(bg=bg, fg=TEXT)
            status.config(bg=bg, fg=SOFT_TEXT)
        else:
            row.config(bg=CARD2, highlightbackground=BORDER)
            name.config(bg=CARD2, fg=TEXT)
            if path in self._failed_files:
                status.config(bg=CARD2, fg=ERROR)
            elif path in self._retouched:
                status.config(bg=CARD2, fg=SUCCESS)
            elif path in self._results:
                status.config(bg=CARD2, fg=ACCENT_CYAN)
            else:
                status.config(bg=CARD2, fg=DIM)

    def _set_file_hover(self, path: str, hovered: bool):
        self._hover_file_path = path if hovered else (None if self._hover_file_path == path else self._hover_file_path)
        self._style_file_row(path)

    def _select_index(self, idx: int):
        if idx < 0 or idx >= len(self._files):
            return
        self._sel = idx
        for path in self._files:
            self._style_file_row(path)
        self._on_select()

    def _remove_selected_file(self):
        if self._sel is None or self._sel >= len(self._files):
            return
        path = self._files.pop(self._sel)
        self._results.pop(path, None)
        self._retouched.pop(path, None)
        self._manual_history.pop(path, None)
        self._manual_history_index.pop(path, None)
        self._failed_files.discard(path)
        self._file_thumb_cache.pop(path, None)
        self._hover_file_path = None

        if not self._files:
            self._sel = None
            self._clear()
            return

        self._sel = min(self._sel, len(self._files) - 1)
        self._refresh_file_gallery()
        self._select_index(self._sel)

    def _make_card(self, parent, title_key):
        f = tk.Frame(parent, bg=CARD, highlightthickness=1,
                     highlightbackground=BORDER_SOFT)
        f._title_key = title_key
        f._title_label = tk.Label(f, text=self._t(title_key), font=("Segoe UI",8,"bold"),
                                  bg=CARD, fg=ACCENT_GOLD)
        f._title_label.pack(pady=(12,6))
        cv = tk.Canvas(f, bg=PREVIEW_BG, highlightthickness=0, bd=0, cursor="crosshair")
        cv.pack(fill="both", expand=True, padx=8, pady=(0,10))
        f._cv   = cv
        f._pil  = None
        f._tkimg = None
        f._bg_tkimg = None
        f._img_id = None
        f._bg_id = None
        f._render_key = None
        f._disp_size = (0, 0)
        f._offset_x = 0
        f._offset_y = 0
        f._pan_anchor = None
        f._txt_id = cv.create_text(10, 10, text=self._t("no_image"),
                                   fill=DIM, font=("Segoe UI",9), anchor="nw")
        f._loading_rect = cv.create_rectangle(0, 0, 0, 0, fill="#08111e", stipple="gray50",
                                              outline="", state="hidden")
        f._loading_text = cv.create_text(0, 0, text=self._t("processing"),
                                         fill=TEXT, font=("Segoe UI",13,"bold"),
                                         state="hidden")
        f._loading_sub = cv.create_text(0, 0, text="Applying background removal",
                                        fill=DIM, font=("Segoe UI",9),
                                        state="hidden")
        cv.bind("<Configure>", lambda e, ff=f: self._cv_resize(ff))
        cv.bind("<MouseWheel>", lambda e, ff=f: self._on_preview_wheel(ff, e))
        cv.bind("<Double-Button-1>", lambda _e: self._fit_preview_zoom())
        cv.bind("<ButtonPress-1>", lambda e, ff=f: self._start_card_pan(ff, e))
        cv.bind("<B1-Motion>", lambda e, ff=f: self._drag_card_pan(ff, e))
        cv.bind("<ButtonRelease-1>", lambda e, ff=f: self._end_card_pan(ff, e))
        cv.bind("<ButtonPress-3>", lambda e, ff=f: self._start_card_pan(ff, e, True))
        cv.bind("<B3-Motion>", lambda e, ff=f: self._drag_card_pan(ff, e, True))
        cv.bind("<ButtonRelease-3>", lambda e, ff=f: self._end_card_pan(ff, e, True))
        return f

    def _cv_resize(self, card):
        """Chamado quando o canvas é redimensionado."""
        try:
            card._title_label.config(wraplength=max(80, card.winfo_width() - 24), justify="center")
        except Exception:
            pass
        if card._pil:
            self._draw_card(card)
        else:
            w = card._cv.winfo_width()
            h = card._cv.winfo_height()
            card._cv.coords(card._txt_id, w//2, h//2)
            card._cv.itemconfig(card._txt_id, anchor="center")
        self._layout_loading_overlay(card)

    def _draw_card(self, card):
        cv = card._cv
        self.update_idletasks()
        w = cv.winfo_width()
        h = cv.winfo_height()
        if w < 20 or h < 20:
            self.after(80, lambda: self._draw_card(card))
            return
        card._cv.itemconfig(card._txt_id, text="")

        bg_key = (w, h)
        bg_tk = self._preview_bg_cache.get(bg_key)
        if bg_tk is None:
            bg_tk = ImageTk.PhotoImage(make_checkerboard(bg_key))
            self._preview_bg_cache[bg_key] = bg_tk
        card._bg_tkimg = bg_tk
        if card._bg_id is None:
            card._bg_id = cv.create_image(0, 0, image=bg_tk, anchor="nw", tags="bg")
        else:
            cv.itemconfig(card._bg_id, image=bg_tk)

        key = (id(card._pil), w, h, round(self._preview_zoom, 3))
        if card._render_key != key:
            rendered = render_preview_image(card._pil, w, h, self._preview_zoom)
            card._tkimg = ImageTk.PhotoImage(rendered)
            card._disp_size = rendered.size
            card._render_key = key
            if card._img_id is None:
                card._img_id = cv.create_image(0, 0, image=card._tkimg, anchor="nw", tags="img")
            else:
                cv.itemconfig(card._img_id, image=card._tkimg)

        self._position_card_image(card)
        self._layout_loading_overlay(card)

    def _set_card(self, card, pil_img, preserve_view=False):
        prev_offset_x = getattr(card, "_offset_x", 0)
        prev_offset_y = getattr(card, "_offset_y", 0)
        card._pil = pil_img
        card._render_key = None
        card._disp_size = (0, 0)
        card._offset_x = prev_offset_x if preserve_view else 0
        card._offset_y = prev_offset_y if preserve_view else 0
        card._pan_anchor = None
        self._draw_card(card)
        self._refresh_manual_ui_state()

    def _clear_card(self, card, msg=None):
        if msg is None:
            msg = self._t("no_image")
        card._pil = None
        card._tkimg = None
        card._bg_tkimg = None
        card._render_key = None
        card._disp_size = (0, 0)
        card._offset_x = 0
        card._offset_y = 0
        card._pan_anchor = None
        if card._img_id is not None:
            card._cv.delete(card._img_id)
            card._img_id = None
        if card._bg_id is not None:
            card._cv.delete(card._bg_id)
            card._bg_id = None
        self._refresh_manual_ui_state()
        w = card._cv.winfo_width() or 100
        h = card._cv.winfo_height() or 100
        card._cv.coords(card._txt_id, w//2, h//2)
        card._cv.itemconfig(card._txt_id, text=msg, anchor="center")
        self._layout_loading_overlay(card)

    def _layout_loading_overlay(self, card):
        cv = card._cv
        w = cv.winfo_width() or 100
        h = cv.winfo_height() or 100
        cv.coords(card._loading_rect, 0, 0, w, h)
        cv.coords(card._loading_text, w // 2, h // 2 - 10)
        cv.coords(card._loading_sub, w // 2, h // 2 + 18)
        cv.tag_raise(card._loading_rect)
        cv.tag_raise(card._loading_text)
        cv.tag_raise(card._loading_sub)

    def _set_preview_loading(self, active: bool, message=None):
        if message is None:
            message = self._t("loading_remove_sub")
        cards = [card for card in (
            getattr(self, "_card_b", None),
            getattr(self, "_card_a", None),
        ) if card]

        if active:
            self._loading_cards = set(cards)
            for card in cards:
                self._layout_loading_overlay(card)
                card._cv.itemconfig(card._loading_rect, state="normal")
                card._cv.itemconfig(card._loading_text, state="normal", text=self._t("processing"))
                card._cv.itemconfig(card._loading_sub, state="normal", text=message)
            self._tick_loading_overlay()
        else:
            for card in cards:
                card._cv.itemconfig(card._loading_rect, state="hidden")
                card._cv.itemconfig(card._loading_text, state="hidden")
                card._cv.itemconfig(card._loading_sub, state="hidden")
            self._loading_cards.clear()
            if self._loading_anim_job:
                self.after_cancel(self._loading_anim_job)
                self._loading_anim_job = None
            self._loading_phase = 0

    def _tick_loading_overlay(self):
        if not self._loading_cards:
            self._loading_anim_job = None
            return
        base = self._t("processing")
        frames = [base, f"{base}.", f"{base}..", f"{base}..."]
        text = frames[self._loading_phase % len(frames)]
        for card in tuple(self._loading_cards):
            try:
                card._cv.itemconfig(card._loading_text, text=text)
            except tk.TclError:
                pass
        self._loading_phase += 1
        self._loading_anim_job = self.after(280, self._tick_loading_overlay)

    def _build_retouch_tab(self, tab):
        ctrl = tk.Frame(tab, bg=CARD2, highlightthickness=1,
                        highlightbackground=BORDER_SOFT)
        ctrl.pack(fill="x", padx=8, pady=8)

        tk.Label(ctrl, text="Retoque Manual de Bordas",
                 font=("Segoe UI",11,"bold"), bg=CARD2, fg=TEXT).pack(
                     anchor="w", padx=14, pady=(12,2))
        tk.Label(ctrl,
                 text="Ajuste fino para remover bordas brancas restantes, sem reprocessar tudo.",
                 font=("Segoe UI",9), bg=CARD2, fg=DIM,
                 wraplength=700, justify="left").pack(anchor="w", padx=14)

        grid = tk.Frame(ctrl, bg=CARD2)
        grid.pack(fill="x", padx=14, pady=(10,4))
        grid.columnconfigure(1, weight=1)

        def row_scale(label, var, from_, to, r):
            tk.Label(grid, text=label, font=("Segoe UI",9),
                     bg=CARD2, fg=TEXT).grid(row=r, column=0, sticky="w", pady=4)
            frm = tk.Frame(grid, bg=CARD2)
            frm.grid(row=r, column=1, sticky="ew", padx=(10,0))
            tk.Scale(frm, variable=var, from_=from_, to=to,
                     orient="horizontal", bg=CARD2, fg=TEXT,
                     highlightthickness=0, troughcolor=CARD,
                     activebackground=ACCENT_ALT, sliderrelief="flat", bd=0,
                     font=("Segoe UI",7)).pack(side="left", fill="x", expand=True)
            tk.Label(frm, textvariable=var, font=("Segoe UI",8),
                     bg=CARD2, fg=DIM, width=4).pack(side="left")

        row_scale("Limiar de branco (quanto remover):", self._thr_ret, 180, 255, 0)
        row_scale("Erosão de borda (px a remover):",    self._erode_ret, 0, 8,  1)

        btns = tk.Frame(ctrl, bg=CARD2)
        btns.pack(fill="x", padx=14, pady=(4,12))
        self._mkbtn(btns, "Aplicar retoque",
                    self._apply_retouch, bg=ACCENT, hover="#86dcff", pady=8,
                    font=("Segoe UI",10,"bold")).pack(side="left")
        tk.Frame(btns, bg=CARD2, width=8).pack(side="left")
        self._mkbtn(btns, "Salvar retocada",
                    self._save_retouched, bg=CARD, hover="#22304a",
                    pady=8).pack(side="left")
        tk.Frame(btns, bg=CARD2, width=8).pack(side="left")
        self._mkbtn(btns, "Reprocessar com matting",
                    self._reprocess, bg=CARD, hover="#22304a",
                    pady=8).pack(side="left")

        prev = tk.Frame(tab, bg=BG)
        prev.pack(fill="both", expand=True, padx=8, pady=(0,8))
        prev.columnconfigure(0, weight=1)
        prev.columnconfigure(1, weight=1)
        prev.rowconfigure(0, weight=1)
        self._rt_card_b = self._make_card(prev, "SEM FUNDO (antes do retoque)")
        self._rt_card_b.grid(row=0, column=0, sticky="nsew", padx=(0,5))
        self._rt_card_a = self._make_card(prev, "APÓS RETOQUE")
        self._rt_card_a.grid(row=0, column=1, sticky="nsew", padx=(5,0))

    # ── Toggle modo ───────────────────────────────────────────
    def _toggle_modo(self):
        simples = self._modo_simples.get()
        self._thr_main.set(215 if simples else max(self._thr_main.get(), 180))
        if simples:
            self._preview_nav_mode = False
            self._quick_tools_open = False
        self._render_mode_toggle()
        self._apply_simple_mode_layout()

    def _toggle_simple_mode(self, _event=None):
        self._modo_simples.set(not self._modo_simples.get())
        self._toggle_modo()

    def _t(self, key: str, **kwargs):
        text = I18N.get(self._lang, I18N["en"]).get(key, key)
        return text.format(**kwargs) if kwargs else text

    def _set_language(self, lang: str):
        if lang not in I18N or self._lang == lang:
            return
        self._lang = lang
        self._refresh_ui_texts()

    def _refresh_language_toggle(self):
        if not hasattr(self, "_btn_lang_en"):
            return
        active_bg = "#243754"
        inactive_bg = CARD2
        active_hover = "#2B4164"
        inactive_hover = "#263446"

        for lang, btn in (("en", self._btn_lang_en), ("pt", self._btn_lang_pt)):
            active = self._lang == lang
            btn.config(text=self._t("lang_en") if lang == "en" else self._t("lang_pt"))
            btn._skin["normal"]["bg"] = active_bg if active else inactive_bg
            btn._skin["hover"]["bg"] = active_hover if active else inactive_hover
            btn._skin["pressed"]["bg"] = active_hover if active else inactive_hover
            self._apply_button_skin(btn)

    def _get_export_format_values(self):
        return {
            "png": self._t("format_png"),
            "webp": self._t("format_webp"),
            "tiff": self._t("format_tiff"),
            "jpg": self._t("format_jpg"),
            "bmp": self._t("format_bmp"),
        }

    def _get_manual_tool_values(self):
        return {
            "none": f"-- {self._t('tool_none')}",
            "restore": f"+ {self._t('tool_restore')}",
            "cut": f"x {self._t('tool_cut')}",
        }

    def _get_brush_shape_values(self):
        return {
            "round": f"O {self._t('shape_round')}",
            "square": f"[] {self._t('shape_square')}",
            "triangle": f"/\\ {self._t('shape_triangle')}",
            "pencil": f".. {self._t('shape_pencil')}",
        }

    def _sync_export_combo(self):
        if not hasattr(self, "_export_combo"):
            return
        values_map = self._get_export_format_values()
        values = [values_map[key] for key in EXPORT_FORMATS]
        self._export_combo.configure(values=values)
        self._export_format.set(values_map.get(self._export_format_key, values_map["png"]))

    def _sync_manual_tool_combo(self):
        if not hasattr(self, "_manual_tool_combo"):
            return
        values_map = self._get_manual_tool_values()
        self._manual_tool_combo.configure(values=[values_map[key] for key in values_map])
        self._manual_tool_combo.set(values_map.get(self._manual_tool.get(), values_map["none"]))

    def _sync_brush_shape_combo(self):
        if not hasattr(self, "_brush_shape_combo"):
            return
        values_map = self._get_brush_shape_values()
        self._brush_shape_combo.configure(values=[values_map[key] for key in values_map])
        self._brush_shape_combo.set(values_map.get(self._brush_shape.get(), values_map["round"]))

    def _on_export_format_change(self, _event=None):
        selected = self._export_format.get()
        for key, label in self._get_export_format_values().items():
            if label == selected:
                self._export_format_key = key
                break

    def _on_manual_tool_change(self, _event=None):
        selected = self._manual_tool_combo.get()
        for key, label in self._get_manual_tool_values().items():
            if label == selected:
                self._manual_tool.set(key)
                break
        self._preview_nav_mode = False
        self._refresh_manual_ui_state()

    def _on_brush_shape_change(self, _event=None):
        selected = self._brush_shape_combo.get()
        for key, label in self._get_brush_shape_values().items():
            if label == selected:
                self._brush_shape.set(key)
                break
        self._refresh_manual_ui_state()

    def _set_manual_tool(self, tool: str):
        self._manual_tool.set(tool)
        self._preview_nav_mode = False
        self._sync_manual_tool_combo()
        self._refresh_manual_ui_state()

    def _set_brush_shape(self, shape: str):
        self._brush_shape.set(shape)
        self._sync_brush_shape_combo()
        self._refresh_manual_ui_state()

    def _refresh_ui_texts(self):
        self.title(self._t("app_title"))
        self._lbl_title.config(text=self._t("header_title"))
        self._lbl_subtitle.config(text=self._t("header_subtitle"))
        self._lbl_mode_title.config(text=self._t("simple_mode"))
        self._lbl_mode_sub.config(text=self._t("simple_mode_sub"))
        self._lbl_left_title.config(text=self._t("your_images"))
        self._lbl_left_sub.config(text=self._t("your_images_sub"))
        self._lbl_left_sub.config(wraplength=230 if self._lang == "en" else 250)
        self._btn_add.config(text=self._t("add"))
        self._btn_folder.config(text=self._t("folder"))
        self._btn_remove_file.config(text=self._t("remove"))
        self._lbl_export_title.config(text=self._t("export"))
        self._btn_change_folder.config(text=self._t("change_folder"))
        self._btn_export_sidebar.config(text=self._t("export_file"))
        self._btn_copy_sidebar.config(text=self._t("copy_image"))
        if self._out_dir is None:
            self._lbl_out.config(text=self._t("same_folder"))
        self._lbl_preview_title.config(text=self._t("preview"))
        self._lbl_preview_sub.config(text=self._t("preview_sub"))
        self._lbl_preview_sub.config(wraplength=360)
        self._btn_view_before.config(text=self._t("before"))
        self._btn_view_after.config(text=self._t("after"))
        self._btn_view_split.config(text=self._t("split"))
        self._btn_fit.config(text=self._t("fit"))
        self._lbl_controls_title.config(text=self._t("adjustments"))
        self._lbl_controls_sub.config(text=self._t("adjustments_sub"))
        self._lbl_controls_sub.config(wraplength=212)
        for key, lbl in self._slider_label_refs.items():
            lbl.config(text=self._t(key))
        if hasattr(self, "_lbl_color_title"):
            self._lbl_color_title.config(text=self._t("bg_colors_title"))
            self._lbl_color_sub.config(text=self._t("bg_colors_sub"), wraplength=180)
            self._lbl_color_tolerance.config(text=self._t("color_tolerance"))
            self._lbl_spill.config(text=self._t("spill_suppress"))
            self._btn_reapply_colors.config(text=self._t("reapply_colors"))
        if hasattr(self, "_lbl_sticker_title"):
            self._lbl_sticker_title.config(text=self._t("sticker_mode"))
            self._lbl_sticker_sub.config(text=self._t("sticker_mode_sub"), wraplength=172)
        if hasattr(self, "_lbl_resize_title"):
            self._lbl_resize_title.config(text=self._t("output_size"))
            self._lbl_resize_sub.config(text=self._t("output_size_sub"), wraplength=160)
            self._resize_enable_chk.config(text=self._t("resize_enable"))
            self._lbl_resize_width.config(text=self._t("width_label"))
            self._lbl_resize_height.config(text=self._t("height_label"))
            self._lbl_resize_lock.config(text=self._t("lock_ratio"))
            self._update_original_dimensions_label()
        if hasattr(self, "_btn_export_resized_orig"):
            self._btn_export_resized_orig.config(text=self._t("export_resized_original"))
        if hasattr(self, "_lbl_manual_title"):
            self._lbl_manual_title.config(text=self._t("manual_tools"))
            self._lbl_manual_sub.config(text=self._t("manual_tools_sub_short"), wraplength=160)
            self._process_selected_chk.config(text=self._t("process_selected_only"))
            self._hair_protect_chk.config(text=self._t("hair_protect"))
            self._lbl_hair_sub.config(text=self._t("hair_protect_sub"), wraplength=160)
            self._lbl_manual_tool.config(text=self._t("manual_tool"))
            self._lbl_brush_shape.config(text=self._t("brush_shape"))
            self._lbl_brush_size.config(text=self._t("brush_size"))
            self._lbl_manual_tip.config(text=self._t("manual_tip"), wraplength=160)
            self._btn_undo.config(text=self._t("undo"))
            self._btn_redo.config(text=self._t("redo"))
            self._sync_manual_tool_combo()
            self._sync_brush_shape_combo()
        self._set_glow_button_text(self._btn_run, self._t("remove_bg"))
        self._btn_refine.config(text=self._t("refine_edges"))
        self._btn_export.config(text=self._t("export_file"))
        self._btn_copy.config(text=self._t("copy_image"))
        self._lbl_simple_note.config(text=self._t("simple_note"), wraplength=212)
        if hasattr(self, "_btn_controls_toggle"):
            self._btn_controls_toggle.config(
                text=">>" if self._controls_collapsed else "<<"
            )
        self._sync_export_combo()
        self._refresh_quick_tools()
        for card in (getattr(self, "_card_b", None), getattr(self, "_card_a", None),
                     getattr(self, "_rt_card_b", None), getattr(self, "_rt_card_a", None)):
            if card and hasattr(card, "_title_label"):
                card._title_label.config(text=self._t(card._title_key))
        self._refresh_file_gallery()
        if self._sel is not None and self._sel < len(self._files):
            self._on_select()
        else:
            self._resolution_text.set(self._t("no_image"))
        self._refresh_language_toggle()
        self._set_status(self._t("ready_status"), SUCCESS)
        self._apply_controls_panel_layout()
        self._refresh_history_buttons()

    def _apply_simple_mode_layout(self):
        if not hasattr(self, "_edge_slider_card"):
            return
        simple = self._modo_simples.get()
        toggle_pairs = (
            (self._edge_slider_card, not simple),
            (self._sticker_card, not simple),
            (self._resize_card, not simple),
            (self._manual_card, not simple),
            (self._btn_refine, not simple),
            (self._lbl_simple_note, simple),
        )
        # Em Modo Simples: oculta controles avançados do filtro de cores (slider + spill + re-apply)
        if hasattr(self, "_color_card") and hasattr(self._color_card, "_color_body"):
            if simple:
                self._color_card._color_body.grid_remove()
            else:
                self._color_card._color_body.grid()
        for widget, show in toggle_pairs:
            if show:
                widget.grid()
            else:
                widget.grid_remove()
        self._update_resize_controls_state()
        if hasattr(self, "_controls_canvas"):
            self.after_idle(lambda: self._controls_canvas.configure(
                scrollregion=self._controls_canvas.bbox("all")
            ))
        self._refresh_quick_tools()
        self._refresh_history_buttons()

    def _toggle_controls_panel(self):
        self._controls_collapsed = not self._controls_collapsed
        self._apply_controls_panel_layout()
        self._update_layout_constraints()
        self._schedule_preview_redraw(immediate=True)

    def _apply_controls_panel_layout(self):
        if not hasattr(self, "_controls_content"):
            return
        if self._controls_collapsed:
            self._controls_content.grid_remove()
            self._controls_header_text.grid_remove()
            self._btn_controls_toggle.config(text=">>")
        else:
            self._controls_content.grid()
            self._controls_header_text.grid()
            self._btn_controls_toggle.config(text="<<")

    def _refresh_quick_tools(self):
        if not hasattr(self, "_quick_tools_wrap"):
            return
        enabled = not self._modo_simples.get()
        self._quick_tools_title.config(text=self._t("quick_tools"))
        self._btn_quick_launcher.config(
            text=self._t("quick_tools_close") if self._quick_tools_open else self._t("quick_tools_open")
        )
        self._btn_quick_move.config(text=self._t("tool_move"))
        self._btn_quick_restore.config(text=self._t("tool_restore"))
        self._btn_quick_cut.config(text=self._t("tool_cut"))
        self._btn_quick_off.config(text=self._t("tool_none"))
        self._btn_quick_undo.config(text=self._t("undo"))
        self._btn_quick_redo.config(text=self._t("redo"))

        if not enabled:
            self._quick_tools_open = False
            self._quick_tools_wrap.place_forget()
            return
        self._quick_tools_wrap.place(relx=1.0, rely=1.0, x=-14, y=-16, anchor="se")
        self._apply_quick_tools_layout()
        self._refresh_history_buttons()

    def _toggle_quick_tools(self):
        self._quick_tools_open = not self._quick_tools_open
        self._apply_quick_tools_layout()

    def _apply_quick_tools_layout(self):
        if not hasattr(self, "_quick_tools_menu"):
            return
        if self._quick_tools_open and not self._modo_simples.get():
            self._quick_tools_menu.pack(anchor="e", pady=(0,8))
            self._btn_quick_launcher.config(text=self._t("quick_tools_close"))
        else:
            self._quick_tools_menu.pack_forget()
            self._btn_quick_launcher.config(text=self._t("quick_tools_open"))
        self._refresh_manual_ui_state()

    def _toggle_expandable_card(self, card):
        if not hasattr(card, "_expanded_var"):
            return
        card._expanded_var.set(not card._expanded_var.get())
        self._apply_expandable_card_state(card)

    def _apply_expandable_card_state(self, card):
        if not hasattr(card, "_expanded_var") or not hasattr(card, "_body"):
            return
        expanded = bool(card._expanded_var.get())
        if expanded:
            card._body.grid()
        else:
            card._body.grid_remove()
        if hasattr(card, "_toggle_label"):
            card._toggle_label.config(text="−" if expanded else "+")
        if hasattr(self, "_controls_canvas"):
            self.after_idle(lambda: self._controls_canvas.configure(
                scrollregion=self._controls_canvas.bbox("all")
            ))

    def _render_mode_toggle(self):
        if not hasattr(self, "_mode_toggle_canvas"):
            return
        cv = self._mode_toggle_canvas
        cv.delete("all")
        on = self._modo_simples.get()
        track_color = ACCENT if on else "#26303C"
        knob_x = 29 if on else 17

        cv.create_oval(4, 4, 24, 24, fill=track_color, outline=track_color)
        cv.create_rectangle(14, 4, 32, 24, fill=track_color, outline=track_color)
        cv.create_oval(22, 4, 42, 24, fill=track_color, outline=track_color)

        cv.create_oval(knob_x - 8, 6, knob_x + 8, 22,
                       fill=TEXT, outline=TEXT)

    def _set_mousewheel_target(self, widget):
        self._mousewheel_target = widget

    def _setup_drag_and_drop(self):
        if not DND_READY:
            return
        for widget in (
            self,
            getattr(self, "_shell", None),
            getattr(self, "_files_canvas", None),
            getattr(self, "_preview_stage", None),
            getattr(self, "_controls_canvas", None),
        ):
            self._register_drop_target(widget)

    def _register_drop_target(self, widget):
        if widget is None or not hasattr(widget, "drop_target_register"):
            return
        try:
            widget.drop_target_register(DND_FILES)
            widget.dnd_bind("<<Drop>>", self._on_drop_files)
        except Exception:
            pass

    def _parse_drop_paths(self, data: str):
        try:
            raw_items = self.tk.splitlist(data)
        except Exception:
            raw_items = [data]

        paths = []
        for item in raw_items:
            path = item.strip()
            if not path:
                continue
            path = path.strip("{}")
            p = Path(path)
            if p.is_dir():
                paths.extend(str(child) for child in p.iterdir() if child.suffix.lower() in EXTS)
            elif p.suffix.lower() in EXTS and p.exists():
                paths.append(str(p))
        return paths

    def _on_drop_files(self, event):
        paths = self._parse_drop_paths(event.data)
        if paths:
            self._add_files(paths)
            self._set_status(self._t("drop_status"), SUCCESS)
        return "break"

    def _on_mousewheel_target(self, event):
        target = self._mousewheel_target
        if target is None:
            return
        step = -1 if event.delta > 0 else 1
        try:
            target.yview_scroll(step, "units")
        except tk.TclError:
            self._mousewheel_target = None
        return "break"

    def _rounded_rect(self, canvas, x1, y1, x2, y2, radius, **kwargs):
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return canvas.create_polygon(points, smooth=True, splinesteps=20, **kwargs)

    def _make_glow_button(self, parent, text, cmd):
        btn = tk.Canvas(parent, height=62, highlightthickness=0, bd=0,
                        bg=CARD, cursor="hand2")
        btn._command = cmd
        btn._glow_text = text
        btn._glow_default_text = text
        btn._glow_state = "normal"
        btn._glow_enabled = True
        btn._glow_loading = False
        btn.bind("<Configure>", lambda _e, b=btn: self._render_glow_button(b))
        btn.bind("<Enter>", lambda _e, b=btn: self._glow_button_event(b, "hover"))
        btn.bind("<Leave>", lambda _e, b=btn: self._glow_button_event(b, "normal"))
        btn.bind("<ButtonPress-1>", lambda _e, b=btn: self._glow_button_event(b, "pressed"))
        btn.bind("<ButtonRelease-1>", lambda e, b=btn: self._glow_button_release(b, e))
        self._render_glow_button(btn)
        return btn

    def _glow_palette(self, state):
        return {
            "normal":  {"glow": "#1C4F8D", "outer": "#2D7FE6", "inner": "#4EA4FF", "text": "#07121F"},
            "hover":   {"glow": "#2768B5", "outer": "#479BFF", "inner": "#68B3FF", "text": "#07121F"},
            "pressed": {"glow": "#123B6E", "outer": "#2D7FDF", "inner": "#3E90F2", "text": "#07101A"},
            "disabled":{"glow": "#10151D", "outer": "#1A2431", "inner": "#202B39", "text": "#6B7788"},
            "loading": {"glow": "#1E548F", "outer": "#357DCE", "inner": "#4C93DD", "text": "#EAF4FF"},
        }[state]

    def _render_glow_button(self, btn):
        btn.delete("all")
        w = max(140, btn.winfo_width() or 140)
        h = max(62, btn.winfo_height() or 62)
        state = "loading" if btn._glow_loading else ("disabled" if not btn._glow_enabled else btn._glow_state)
        pal = self._glow_palette(state)
        btn.configure(bg=CARD)
        self._rounded_rect(btn, 10, 12, w - 10, h - 4, 18, fill=pal["glow"], outline="", stipple="gray50")
        self._rounded_rect(btn, 6, 8, w - 6, h - 8, 18, fill=pal["outer"], outline="")
        self._rounded_rect(btn, 8, 10, w - 8, h - 10, 16, fill=pal["inner"], outline="")
        btn.create_text(w // 2, h // 2, text=btn._glow_text, fill=pal["text"],
                        font=("Segoe UI", 13, "bold"))

    def _glow_button_event(self, btn, state):
        if not btn._glow_enabled or btn._glow_loading:
            return
        btn._glow_state = state
        self._render_glow_button(btn)

    def _glow_button_release(self, btn, event):
        if not btn._glow_enabled or btn._glow_loading:
            return
        x, y = event.x, event.y
        inside = 0 <= x <= btn.winfo_width() and 0 <= y <= btn.winfo_height()
        btn._glow_state = "hover" if inside else "normal"
        self._render_glow_button(btn)
        if inside and callable(btn._command):
            btn._command()

    def _set_glow_button_enabled(self, btn, enabled: bool):
        btn._glow_enabled = enabled
        btn._glow_loading = False
        btn._glow_state = "normal"
        self._render_glow_button(btn)

    def _set_glow_button_loading(self, btn, loading: bool, text: str | None = None):
        btn._glow_loading = loading
        btn._glow_text = text or btn._glow_default_text
        if not loading:
            btn._glow_text = btn._glow_default_text
        self._render_glow_button(btn)

    def _set_glow_button_text(self, btn, text: str):
        btn._glow_text = text
        btn._glow_default_text = text
        self._render_glow_button(btn)

    def _setup_button_skin(self, btn, variant="secondary"):
        skins = {
            "primary": {
                "normal":   {"bg": "#3994FF", "fg": "#07121F", "border": "#61AEFF"},
                "hover":    {"bg": "#4AA1FF", "fg": "#07121F", "border": "#84C1FF"},
                "pressed":  {"bg": "#2E84EA", "fg": "#06101C", "border": "#4EA0FF"},
                "disabled": {"bg": "#1A2431", "fg": "#6F7C8F", "border": "#273344"},
                "loading":  {"bg": "#2C6FB5", "fg": "#EAF4FF", "border": "#4E8FD4"},
            },
            "secondary": {
                "normal":   {"bg": CARD2, "fg": TEXT, "border": BORDER},
                "hover":    {"bg": "#202938", "fg": TEXT, "border": BORDER_SOFT},
                "pressed":  {"bg": "#253042", "fg": TEXT, "border": BORDER_SOFT},
                "disabled": {"bg": "#141B25", "fg": "#627083", "border": BORDER},
                "loading":  {"bg": "#1E2633", "fg": DIM, "border": BORDER},
            },
        }
        btn._skin = skins[variant]
        btn._skin_variant = variant
        btn._skin_force_state = None
        btn._skin_text_default = btn.cget("text")
        btn.configure(disabledforeground=btn._skin["disabled"]["fg"])
        self._apply_button_skin(btn)

        def _enter(_):
            if btn.cget("state") == "disabled" or btn._skin_force_state == "loading":
                return
            self._apply_button_skin(btn, "hover")

        def _leave(_):
            if btn.cget("state") == "disabled" or btn._skin_force_state == "loading":
                self._apply_button_skin(btn)
                return
            self._apply_button_skin(btn, "normal")

        def _press(_):
            if btn.cget("state") == "disabled" or btn._skin_force_state == "loading":
                return
            self._apply_button_skin(btn, "pressed")

        def _release(_):
            if btn.cget("state") == "disabled" or btn._skin_force_state == "loading":
                self._apply_button_skin(btn)
                return
            self._apply_button_skin(btn, "hover")

        btn.bind("<Enter>", _enter, add="+")
        btn.bind("<Leave>", _leave, add="+")
        btn.bind("<ButtonPress-1>", _press, add="+")
        btn.bind("<ButtonRelease-1>", _release, add="+")

    def _apply_button_skin(self, btn, visual_state=None):
        if not hasattr(btn, "_skin"):
            return
        state = visual_state or btn._skin_force_state
        if state is None:
            state = "disabled" if btn.cget("state") == "disabled" else "normal"
        palette = btn._skin[state]
        btn.configure(
            bg=palette["bg"],
            fg=palette["fg"],
            activebackground=palette["bg"],
            activeforeground=palette["fg"],
            highlightbackground=palette["border"],
            highlightcolor=palette["border"],
            disabledforeground=palette["fg"],
        )

    def _set_button_enabled(self, btn, enabled: bool):
        btn._skin_force_state = None
        btn.configure(state="normal" if enabled else "disabled")
        self._apply_button_skin(btn)

    def _set_button_loading(self, btn, loading: bool, text: str | None = None):
        if loading:
            btn._skin_force_state = "loading"
            btn.configure(state="disabled", text=text or btn._skin_text_default)
            self._apply_button_skin(btn, "loading")
        else:
            btn._skin_force_state = None
            btn.configure(state="normal", text=btn._skin_text_default)
            self._apply_button_skin(btn)

    def _set_secondary_buttons_enabled(self, enabled: bool):
        for btn in (
            getattr(self, "_btn_refine", None),
            getattr(self, "_btn_export", None),
            getattr(self, "_btn_copy", None),
            getattr(self, "_btn_export_sidebar", None),
            getattr(self, "_btn_copy_sidebar", None),
        ):
            if btn is not None:
                self._set_button_enabled(btn, enabled)
        self._refresh_history_buttons()

    # ── Helpers ───────────────────────────────────────────────
    def _mkbtn(self, parent, text, cmd, bg=CARD2, fg=TEXT,
               hover=None, pady=6, font=("Segoe UI",9), padx=10):
        btn = tk.Button(parent, text=text, command=cmd,
                        bg=bg, fg=fg,
                        activebackground=hover or bg, activeforeground=fg,
                        font=font, relief="flat", bd=0,
                        padx=padx, pady=pady, cursor="hand2",
                        highlightthickness=1,
                        highlightbackground=BORDER,
                        highlightcolor=BORDER)
        hover_color = hover or bg
        self._setup_button_skin(btn, "secondary")
        btn._skin["normal"]["bg"] = bg
        btn._skin["normal"]["fg"] = fg
        btn._skin["hover"]["bg"] = hover_color
        btn._skin["pressed"]["bg"] = hover_color
        self._apply_button_skin(btn)
        return btn

    def _center(self):
        self.update_idletasks()
        w,h = self.winfo_width(), self.winfo_height()
        sw,sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw-w)//2}+{(sh-h)//2}")

    def _on_root_configure(self, event):
        if event.widget is self:
            self._update_layout_constraints()

    def _update_layout_constraints(self):
        if not hasattr(self, "_shell"):
            return
        total = max(960, self.winfo_width() - 44)
        collapsed = getattr(self, "_controls_collapsed", False)

        if total < 1180:
            left = 210
            right = 56 if collapsed else 250
            center = 360
            outer_pad = 12
        elif total < 1360:
            left = 220
            right = 56 if collapsed else 270
            center = 420
            outer_pad = 14
        else:
            left = 232
            right = 56 if collapsed else 286
            center = 480
            outer_pad = 16

        self._shell.configure(padx=outer_pad, pady=outer_pad)
        self._shell.columnconfigure(0, minsize=left)
        self._shell.columnconfigure(1, minsize=center)
        self._shell.columnconfigure(2, minsize=right)
        if hasattr(self, "_controls_panel"):
            self._controls_panel.configure(width=right)

    def _set_status(self, msg, cor=DIM):
        self._lbl_status.config(text=msg, fg=cor)

    def _close_app(self):
        if self._closing:
            return
        self._closing = True
        self._stop_requested.set()
        self._processing = False
        try:
            self.withdraw()
        except tk.TclError:
            pass
        self.after(120, self._force_exit)

    def _force_exit(self):
        try:
            self.quit()
        except tk.TclError:
            pass
        try:
            self.destroy()
        except tk.TclError:
            pass
        os._exit(0)

    def _on_left_frame_configure(self, _=None):
        self._refresh_left_scroll()

    def _on_left_canvas_configure(self, event):
        self._left_canvas.itemconfigure(self._left_window, width=event.width)
        wrap = max(180, event.width - 24)
        if hasattr(self, "_lbl_out"):
            self._lbl_out.config(wraplength=wrap)
        if hasattr(self, "_lbl_resize_orig"):
            self._lbl_resize_orig.config(wraplength=wrap)
        self._refresh_left_scroll()

    def _refresh_left_scroll(self):
        if hasattr(self, "_left_canvas"):
            bbox = self._left_canvas.bbox("all")
            if bbox:
                self._left_canvas.configure(scrollregion=bbox)

    def _pointer_inside_widget(self, widget):
        if not widget:
            return False
        try:
            x = self.winfo_pointerx()
            y = self.winfo_pointery()
            wx = widget.winfo_rootx()
            wy = widget.winfo_rooty()
            ww = widget.winfo_width()
            wh = widget.winfo_height()
        except tk.TclError:
            return False
        return wx <= x <= wx + ww and wy <= y <= wy + wh

    def _on_global_mousewheel(self, event):
        if not hasattr(self, "_left_canvas"):
            return
        if not self._pointer_inside_widget(self._left_outer):
            return
        if self._pointer_inside_widget(getattr(self, "_card_b", None)._cv
                                       if getattr(self, "_card_b", None) else None):
            return
        if self._pointer_inside_widget(getattr(self, "_card_a", None)._cv
                                       if getattr(self, "_card_a", None) else None):
            return
        step = -1 if event.delta > 0 else 1
        self._left_canvas.yview_scroll(step, "units")
        return "break"

    def _set_initial_sidebar_width(self):
        if not hasattr(self, "_paned"):
            return
        try:
            total = self._paned.winfo_width()
            width = min(380, max(290, total // 3))
            self._paned.sash_place(0, width, 0)
        except tk.TclError:
            pass

    def _clamp_sidebar_width(self, _=None):
        if not hasattr(self, "_paned"):
            return
        try:
            total = self._paned.winfo_width()
            x, y = self._paned.sash_coord(0)
            min_x = 260
            max_x = max(min_x, total - 420)
            x = max(min_x, min(x, max_x))
            self._paned.sash_place(0, x, y)
        except tk.TclError:
            pass

    def _update_resize_section(self):
        if not hasattr(self, "_resize_panel") or not hasattr(self, "_btn_resize_section"):
            return
        if self._resize_section_open:
            self._resize_panel.pack(fill="x", pady=(2,0))
            self._btn_resize_section.config(text="▾")
        else:
            self._resize_panel.pack_forget()
            self._btn_resize_section.config(text="▸")
        self._refresh_left_scroll()

    def _toggle_resize_section(self):
        self._resize_section_open = not self._resize_section_open
        self._update_resize_section()

    def _position_card_image(self, card):
        cv = card._cv
        w = cv.winfo_width()
        h = cv.winfo_height()
        iw, ih = card._disp_size

        if card._bg_id is not None:
            cv.coords(card._bg_id, 0, 0)

        if not card._img_id or iw <= 0 or ih <= 0:
            return

        if iw <= w:
            x = (w - iw) // 2
            card._offset_x = x
        else:
            min_x = w - iw
            x = min(0, max(min_x, int(card._offset_x)))
            card._offset_x = x

        if ih <= h:
            y = (h - ih) // 2
            card._offset_y = y
        else:
            min_y = h - ih
            y = min(0, max(min_y, int(card._offset_y)))
            card._offset_y = y

        cv.coords(card._img_id, card._offset_x, card._offset_y)
        cv.tag_lower(card._bg_id)
        cv.tag_raise(card._img_id)
        cv.config(cursor="fleur" if self._card_overflows(card) else "crosshair")

    def _card_overflows(self, card):
        w = card._cv.winfo_width()
        h = card._cv.winfo_height()
        iw, ih = card._disp_size
        return iw > w or ih > h

    def _reset_history(self, path: str, img: Image.Image | None):
        if img is None:
            self._manual_history.pop(path, None)
            self._manual_history_index.pop(path, None)
        else:
            self._manual_history[path] = [img.convert("RGBA").copy()]
            self._manual_history_index[path] = 0
        self._refresh_history_buttons()

    def _push_history_snapshot(self, path: str, img: Image.Image):
        snapshot = img.convert("RGBA").copy()
        history = self._manual_history.setdefault(path, [])
        idx = self._manual_history_index.get(path, len(history) - 1)
        if idx < len(history) - 1:
            history[:] = history[: idx + 1]
        if history and np.array_equal(np.array(history[-1]), np.array(snapshot)):
            self._manual_history_index[path] = len(history) - 1
            self._refresh_history_buttons()
            return
        history.append(snapshot)
        if len(history) > 30:
            history.pop(0)
        self._manual_history_index[path] = len(history) - 1
        self._refresh_history_buttons()

    def _can_undo_manual(self):
        if self._sel is None or self._sel >= len(self._files):
            return False
        path = self._files[self._sel]
        return self._manual_history_index.get(path, 0) > 0

    def _can_redo_manual(self):
        if self._sel is None or self._sel >= len(self._files):
            return False
        path = self._files[self._sel]
        history = self._manual_history.get(path, [])
        return self._manual_history_index.get(path, 0) < len(history) - 1

    def _restore_history_state(self, path: str):
        history = self._manual_history.get(path)
        idx = self._manual_history_index.get(path, 0)
        if not history or idx < 0 or idx >= len(history):
            return
        restored = history[idx].copy()
        self._retouched[path] = restored
        if hasattr(self, "_card_a") and self._sel is not None and self._files[self._sel] == path:
            self._set_card(self._card_a, restored)
            if self._rt_card_a:
                self._set_card(self._rt_card_a, restored)
        self._style_file_row(path)
        self._refresh_history_buttons()

    def _undo_manual_edit(self):
        if not self._can_undo_manual():
            self._set_status(self._t("undo_empty"), DIM)
            return
        path = self._files[self._sel]
        self._manual_history_index[path] -= 1
        self._restore_history_state(path)
        self._set_status(self._t("undo_done"), ACCENT_CYAN)

    def _redo_manual_edit(self):
        if not self._can_redo_manual():
            self._set_status(self._t("redo_empty"), DIM)
            return
        path = self._files[self._sel]
        self._manual_history_index[path] += 1
        self._restore_history_state(path)
        self._set_status(self._t("redo_done"), ACCENT_CYAN)

    def _undo_shortcut(self, _event=None):
        self._undo_manual_edit()
        return "break"

    def _redo_shortcut(self, _event=None):
        self._redo_manual_edit()
        return "break"

    def _refresh_history_buttons(self):
        undo_enabled = self._can_undo_manual()
        redo_enabled = self._can_redo_manual()
        for btn in (getattr(self, "_btn_undo", None), getattr(self, "_btn_quick_undo", None)):
            if btn is not None:
                self._set_button_enabled(btn, undo_enabled)
        for btn in (getattr(self, "_btn_redo", None), getattr(self, "_btn_quick_redo", None)):
            if btn is not None:
                self._set_button_enabled(btn, redo_enabled)

    def _toggle_preview_nav_mode(self):
        self._preview_nav_mode = not self._preview_nav_mode
        self._refresh_manual_ui_state()

    def _refresh_manual_ui_state(self):
        if hasattr(self, "_card_a") and getattr(self._card_a, "_cv", None):
            if self._preview_nav_mode:
                cursor = "fleur"
            elif self._manual_edit_active(self._card_a):
                cursor = "crosshair"
            else:
                cursor = "fleur" if self._card_overflows(self._card_a) else "crosshair"
            self._card_a._cv.config(cursor=cursor)

        if hasattr(self, "_btn_quick_move"):
            active_bg = "#243754" if self._preview_nav_mode else CARD
            hover_bg = "#2B4164" if self._preview_nav_mode else "#202938"
            for btn in (self._btn_quick_move,):
                btn._skin["normal"]["bg"] = active_bg
                btn._skin["hover"]["bg"] = hover_bg
                btn._skin["pressed"]["bg"] = hover_bg
                self._apply_button_skin(btn)

        tool_buttons = {
            "restore": getattr(self, "_btn_quick_restore", None),
            "cut": getattr(self, "_btn_quick_cut", None),
            "none": getattr(self, "_btn_quick_off", None),
        }
        for key, btn in tool_buttons.items():
            if btn is None:
                continue
            active = self._manual_tool.get() == key and not self._preview_nav_mode
            btn._skin["normal"]["bg"] = "#243754" if active else CARD
            btn._skin["hover"]["bg"] = "#2B4164" if active else "#202938"
            btn._skin["pressed"]["bg"] = "#2B4164" if active else "#202938"
            self._apply_button_skin(btn)

        shape_buttons = {
            "round": getattr(self, "_btn_shape_round", None),
            "square": getattr(self, "_btn_shape_square", None),
            "triangle": getattr(self, "_btn_shape_triangle", None),
            "pencil": getattr(self, "_btn_shape_pencil", None),
        }
        for key, btn in shape_buttons.items():
            if btn is None:
                continue
            active = self._brush_shape.get() == key
            btn._skin["normal"]["bg"] = "#243754" if active else CARD
            btn._skin["hover"]["bg"] = "#2B4164" if active else "#202938"
            btn._skin["pressed"]["bg"] = "#2B4164" if active else "#202938"
            self._apply_button_skin(btn)

    def _manual_edit_active(self, card):
        return (
            not self._modo_simples.get()
            and card is getattr(self, "_card_a", None)
            and self._manual_tool.get() != "none"
            and not self._preview_nav_mode
            and self._sel is not None
            and self._sel < len(self._files)
            and (self._retouched.get(self._files[self._sel]) or self._results.get(self._files[self._sel])) is not None
        )

    def _ensure_manual_original(self, path: str):
        if self._manual_original_path != path or self._manual_original_rgba is None:
            self._manual_original_rgba = Image.open(path).convert("RGBA")
            self._manual_original_path = path
        return self._manual_original_rgba

    def _canvas_to_image_coords(self, card, x: int, y: int):
        iw, ih = card._disp_size
        if iw <= 0 or ih <= 0 or not getattr(card, "_pil", None):
            return None
        local_x = x - card._offset_x
        local_y = y - card._offset_y
        if local_x < 0 or local_y < 0 or local_x > iw or local_y > ih:
            return None
        px = int(local_x * card._pil.width / max(iw, 1))
        py = int(local_y * card._pil.height / max(ih, 1))
        px = min(max(px, 0), card._pil.width - 1)
        py = min(max(py, 0), card._pil.height - 1)
        return px, py

    def _iter_brush_points(self, start, end, step):
        x1, y1 = start
        x2, y2 = end
        dx = x2 - x1
        dy = y2 - y1
        dist = max(abs(dx), abs(dy))
        if dist <= 0:
            return [start]
        points = []
        steps = max(1, int(dist / max(step, 1)))
        for i in range(steps + 1):
            t = i / steps
            points.append((round(x1 + dx * t), round(y1 + dy * t)))
        return points

    def _draw_brush_stamp(self, draw, x: int, y: int, size: int, shape: str):
        half = max(1, size // 2)
        if shape == "pencil":
            half = max(1, size // 5)
            draw.ellipse((x - half, y - half, x + half, y + half), fill=255)
        elif shape == "square":
            draw.rectangle((x - half, y - half, x + half, y + half), fill=255)
        elif shape == "triangle":
            draw.polygon([(x, y - half), (x - half, y + half), (x + half, y + half)], fill=255)
        else:
            draw.ellipse((x - half, y - half, x + half, y + half), fill=255)

    def _apply_manual_brush(self, path: str, start, end=None):
        current = (self._retouched.get(path) or self._results.get(path))
        if current is None:
            return
        current = current.convert("RGBA")
        mask = Image.new("L", current.size, 0)
        draw = ImageDraw.Draw(mask)
        size = int(self._brush_size.get())
        shape = self._brush_shape.get()
        points = [start] if end is None else self._iter_brush_points(start, end, max(1, size // 4))
        for px, py in points:
            self._draw_brush_stamp(draw, px, py, size, shape)

        if self._manual_tool.get() == "restore":
            original = self._ensure_manual_original(path)
            edited = Image.composite(original, current, mask)
        else:
            arr = np.array(current, dtype=np.uint8)
            mask_arr = np.array(mask, dtype=np.uint8)
            arr[mask_arr > 0, 3] = 0
            edited = Image.fromarray(arr, "RGBA")

        edited = sanitizar_rgb_transparente(edited)
        self._retouched[path] = edited
        self._set_card(self._card_a, edited)
        if self._rt_card_a:
            self._set_card(self._rt_card_a, edited)
        self._style_file_row(path)

    def _start_manual_edit(self, card, event):
        coords = self._canvas_to_image_coords(card, event.x, event.y)
        if coords is None or self._sel is None:
            self._manual_drag_last = None
            return
        path = self._files[self._sel]
        current = self._retouched.get(path) or self._results.get(path)
        if current is not None:
            self._push_history_snapshot(path, current)
        self._manual_drag_last = coords
        self._apply_manual_brush(path, coords)

    def _drag_manual_edit(self, card, event):
        coords = self._canvas_to_image_coords(card, event.x, event.y)
        if coords is None or self._manual_drag_last is None or self._sel is None:
            return
        path = self._files[self._sel]
        self._apply_manual_brush(path, self._manual_drag_last, coords)
        self._manual_drag_last = coords

    def _finish_manual_edit(self):
        if self._sel is not None and self._sel < len(self._files):
            path = self._files[self._sel]
            current = self._retouched.get(path) or self._results.get(path)
            if current is not None:
                self._push_history_snapshot(path, current)
        self._manual_drag_last = None
        self._refresh_history_buttons()

    def _should_force_pan(self, card, event=None, force_pan=False):
        shift_pressed = bool(event and (event.state & 0x0001))
        return force_pan or shift_pressed or (card is getattr(self, "_card_a", None) and self._preview_nav_mode)

    def _start_card_pan(self, card, event, force_pan=False):
        if self._manual_edit_active(card) and not self._should_force_pan(card, event, force_pan):
            self._start_manual_edit(card, event)
            return
        if not getattr(card, "_pil", None) or not self._card_overflows(card):
            card._pan_anchor = None
            return
        card._pan_anchor = (event.x, event.y, card._offset_x, card._offset_y)
        card._cv.config(cursor="fleur")

    def _drag_card_pan(self, card, event, force_pan=False):
        if self._manual_edit_active(card) and not self._should_force_pan(card, event, force_pan):
            self._drag_manual_edit(card, event)
            return
        if not card._pan_anchor:
            return
        start_x, start_y, base_x, base_y = card._pan_anchor
        card._offset_x = base_x + (event.x - start_x)
        card._offset_y = base_y + (event.y - start_y)
        self._position_card_image(card)

    def _end_card_pan(self, card, _event, force_pan=False):
        if self._manual_edit_active(card) and not force_pan:
            self._finish_manual_edit()
            return
        card._pan_anchor = None
        self._refresh_manual_ui_state()

    def _change_preview_zoom(self, delta):
        old_zoom = self._preview_zoom
        new_zoom = min(6.0, max(0.2, self._preview_zoom + delta))
        if abs(new_zoom - old_zoom) < 1e-6:
            return
        factor = new_zoom / max(old_zoom, 1e-6)
        for card in (getattr(self, "_card_b", None),
                     getattr(self, "_card_a", None),
                     getattr(self, "_rt_card_b", None),
                     getattr(self, "_rt_card_a", None)):
            if not card or not getattr(card, "_pil", None):
                continue
            cv = card._cv
            cw = cv.winfo_width()
            ch = cv.winfo_height()
            iw, ih = card._disp_size
            if iw > 0:
                focus_x = cw / 2 - card._offset_x
                card._offset_x = cw / 2 - focus_x * factor
            if ih > 0:
                focus_y = ch / 2 - card._offset_y
                card._offset_y = ch / 2 - focus_y * factor
        self._preview_zoom = new_zoom
        self._zoom_text.set(f"{round(self._preview_zoom * 100)}%")
        self._schedule_preview_redraw()

    def _fit_preview_zoom(self):
        self._preview_zoom = 1.0
        self._zoom_text.set("100%")
        for card in (getattr(self, "_card_b", None),
                     getattr(self, "_card_a", None),
                     getattr(self, "_rt_card_b", None),
                     getattr(self, "_rt_card_a", None)):
            if card:
                card._offset_x = 0
                card._offset_y = 0
                card._pan_anchor = None
        self._schedule_preview_redraw(immediate=True)

    def _on_preview_wheel(self, _card, event):
        self._change_preview_zoom(0.1 if event.delta > 0 else -0.1)
        return "break"

    def _schedule_preview_redraw(self, immediate=False):
        if self._preview_redraw_job:
            self.after_cancel(self._preview_redraw_job)
            self._preview_redraw_job = None
        if immediate:
            self._refresh_preview_cards()
        else:
            self._preview_redraw_job = self.after(18, self._flush_preview_redraw)

    def _flush_preview_redraw(self):
        self._preview_redraw_job = None
        self._refresh_preview_cards()

    def _refresh_preview_cards(self):
        for card in (getattr(self, "_card_b", None),
                     getattr(self, "_card_a", None),
                     getattr(self, "_rt_card_b", None),
                     getattr(self, "_rt_card_a", None)):
            if card and getattr(card, "_pil", None):
                self._draw_card(card)

    def _parse_positive_int(self, value):
        try:
            n = int(str(value).strip())
        except (TypeError, ValueError, tk.TclError):
            return None
        return n if n > 0 else None

    def _set_resize_fields(self, width: int | None, height: int | None):
        self._resize_syncing = True
        self._resize_width.set("" if not width else str(width))
        self._resize_height.set("" if not height else str(height))
        self._resize_syncing = False

    def _sync_resize_pair(self, changed: str):
        if self._resize_syncing or not self._resize_lock.get():
            return
        if self._orig_width <= 0 or self._orig_height <= 0:
            return

        width = self._parse_positive_int(self._resize_width.get())
        height = self._parse_positive_int(self._resize_height.get())
        self._resize_syncing = True
        if changed == "width" and width:
            new_h = max(1, round(width * self._orig_height / self._orig_width))
            self._resize_height.set(str(new_h))
        elif changed == "height" and height:
            new_w = max(1, round(height * self._orig_width / self._orig_height))
            self._resize_width.set(str(new_w))
        self._resize_syncing = False

    def _on_resize_width_change(self, *_):
        self._sync_resize_pair("width")
        self._refresh_selected_info()

    def _on_resize_height_change(self, *_):
        self._sync_resize_pair("height")
        self._refresh_selected_info()

    def _toggle_resize_lock(self):
        travado = not self._resize_lock.get()
        self._resize_lock.set(travado)
        if hasattr(self, "_btn_resize_lock"):
            self._btn_resize_lock.config(text="🔒" if travado else "🔓")
        self._update_resize_controls_state()
        if travado:
            self._sync_resize_pair("width")

    def _on_resize_toggle(self):
        if self._resize_enabled.get() and self._orig_width > 0 and self._orig_height > 0:
            if not self._parse_positive_int(self._resize_width.get()) or not self._parse_positive_int(self._resize_height.get()):
                self._set_resize_fields(self._orig_width, self._orig_height)
        self._update_resize_controls_state()
        self._refresh_selected_info()

    def _update_resize_controls_state(self):
        active = (
            hasattr(self, "_entry_resize_width")
            and self._resize_enabled.get()
            and not self._modo_simples.get()
        )
        for entry in (getattr(self, "_entry_resize_width", None), getattr(self, "_entry_resize_height", None)):
            if entry is not None:
                entry.config(state="normal" if active else "disabled")
        if hasattr(self, "_btn_resize_lock"):
            self._set_button_enabled(self._btn_resize_lock, active)
        if hasattr(self, "_btn_export_resized_orig"):
            self._set_button_enabled(self._btn_export_resized_orig, active)

    def _update_original_dimensions_label(self):
        if not hasattr(self, "_lbl_resize_orig"):
            return
        if self._orig_width > 0 and self._orig_height > 0:
            self._lbl_resize_orig.config(
                text=self._t("original_size", width=self._orig_width, height=self._orig_height)
            )
        else:
            self._lbl_resize_orig.config(text=self._t("original_select"))

    def _apply_resize_multiplier(self, multiplier: int):
        if self._orig_width <= 0 or self._orig_height <= 0:
            messagebox.showinfo("Nothing selected", "Select an image first.")
            return
        self._set_resize_fields(self._orig_width * multiplier,
                                self._orig_height * multiplier)
        self._refresh_selected_info()

    def _set_original_dimensions(self, width: int, height: int):
        self._orig_width = width
        self._orig_height = height
        self._update_original_dimensions_label()
        # Só preenche automaticamente se o resize NÃO estiver ativo com valores do usuário
        # (evita resetar dimensões personalizadas ao re-processar a imagem)
        if not self._resize_enabled.get():
            self._set_resize_fields(width, height)
        self._update_resize_controls_state()

    def _clear_original_dimensions(self):
        self._orig_width = 0
        self._orig_height = 0
        self._update_original_dimensions_label()
        self._set_resize_fields(None, None)
        self._update_resize_controls_state()

    def _get_resize_dimensions(self):
        if self._modo_simples.get() or not self._resize_enabled.get():
            return None, None
        width = self._parse_positive_int(self._resize_width.get())
        height = self._parse_positive_int(self._resize_height.get())
        if not width or not height:
            return None, None
        return width, height

    def _refresh_selected_info(self):
        if self._sel is None or self._sel >= len(self._files):
            self._resolution_text.set(self._t("no_image"))
            self._lbl_info.config(text="")
            return
        path = self._files[self._sel]
        try:
            img = Image.open(path)
            info = f"{img.width}×{img.height}px  |  {fmt_size(os.path.getsize(path))}"
            out_w, out_h = self._get_resize_dimensions()
            if out_w and out_h:
                info += f"  |  export: {out_w}×{out_h}px"
            self._lbl_info.config(text=info)
            self._resolution_text.set(f"{img.width} × {img.height}px")
        except Exception:
            pass

    # ── Arquivos ──────────────────────────────────────────────
    def _add_files(self, files=None):
        if files is None:
            files = filedialog.askopenfilenames(
                title=self._t("select_images"),
                filetypes=[(self._t("images_filetype"),"*.png *.jpg *.jpeg *.webp *.bmp *.tiff *.tif"),
                           (self._t("all_files"),"*.*")])
        added = 0
        first_new_idx = None
        for f in files:
            if f not in self._files:
                if first_new_idx is None:
                    first_new_idx = len(self._files)
                self._files.append(f)
                added += 1
        if added:
            self._refresh_file_gallery()
            t = len(self._files)
            self._set_status(self._t("queue_status", count=t))
            self._lbl_count.config(text=f"0/{t}")
            if self._sel is None and first_new_idx is not None:
                self.after(0, lambda idx=first_new_idx: self._select_index(idx))

    def _add_folder(self):
        pasta = filedialog.askdirectory(title=self._t("select_folder"))
        if pasta:
            self._add_files([str(p) for p in Path(pasta).iterdir()
                             if p.suffix.lower() in EXTS])

    def _clear(self):
        self._files.clear(); self._results.clear(); self._retouched.clear()
        self._manual_history.clear(); self._manual_history_index.clear()
        self._failed_files.clear()
        self._file_thumb_cache.clear()
        self._manual_original_path = None
        self._manual_original_rgba = None
        self._refresh_file_gallery()
        for c in (self._card_b, self._card_a, self._rt_card_b, self._rt_card_a):
            if c:
                self._clear_card(c)
        self._sel = None
        self._clear_original_dimensions()
        self._fit_preview_zoom()
        self._set_secondary_buttons_enabled(False)
        if hasattr(self, "_btn_remove_file"):
            self._set_button_enabled(self._btn_remove_file, False)
        self._lbl_info.config(text="")
        self._resolution_text.set(self._t("no_image"))
        self._prog["value"] = 0
        self._lbl_count.config(text="0/0")
        self._refresh_quick_tools()
        self._refresh_history_buttons()

    def _choose_out(self):
        pasta = filedialog.askdirectory(title=self._t("choose_export_folder"))
        if pasta:
            self._out_dir = pasta
            self._lbl_out.config(text=str(Path(pasta)))

    def _on_select(self, _=None):
        if self._sel is None or self._sel >= len(self._files):
            return
        path = self._files[self._sel]
        self._style_file_row(path)
        if hasattr(self, "_btn_remove_file"):
            self._set_button_enabled(self._btn_remove_file, True)

        try:
            img = Image.open(path)
            self._set_card(self._card_b, img)
            self._set_original_dimensions(img.width, img.height)
            self._manual_original_path = path
            self._manual_original_rgba = img.convert("RGBA")
            self._refresh_selected_info()
            # Detecta cores do fundo e atualiza amostras em idle (não bloqueia a UI)
            self.after_idle(lambda i=img.copy(): self._update_color_swatches(i))
        except Exception: pass

        result = self._retouched.get(path) or self._results.get(path)
        if result:
            if path not in self._manual_history:
                self._reset_history(path, result)
            self._set_card(self._card_a, result)
            if self._rt_card_b:
                self._set_card(self._rt_card_b, self._results.get(path, result))
            self._set_secondary_buttons_enabled(True)
        else:
            self._clear_card(self._card_a, self._t("not_processed"))
            if self._rt_card_b:
                self._clear_card(self._rt_card_b)
            if self._rt_card_a:
                self._clear_card(self._rt_card_a)
            self._set_secondary_buttons_enabled(False)
        self._refresh_quick_tools()
        self._refresh_history_buttons()

    # ── Processamento ─────────────────────────────────────────
    def _get_processing_targets(self):
        if self._process_selected_only.get():
            if self._sel is None or self._sel >= len(self._files):
                messagebox.showinfo(self._t("nothing_selected_title"), self._t("nothing_selected_msg"))
                return []
            return [(self._sel, self._files[self._sel], True)]

        targets = []
        for idx, path in enumerate(self._files):
            needs_processing = (
                path not in self._results
                and path not in self._retouched
            ) or path in self._failed_files
            if needs_processing:
                targets.append((idx, path, False))
        if not targets and self._sel is not None and self._sel < len(self._files):
            path = self._files[self._sel]
            if path in self._results or path in self._retouched:
                self._set_status(self._t("reprocess_selected_status"), ACCENT_CYAN)
                return [(self._sel, path, True)]
        return targets

    def _start(self):
        if self._closing or self._stop_requested.is_set():
            return
        if not rembg_pronto: return
        if not self._files:
            messagebox.showwarning(self._t("no_images_title"), self._t("no_images_msg")); return
        if self._processing: return
        targets = self._get_processing_targets()
        if not targets:
            messagebox.showinfo(self._t("no_pending_title"), self._t("no_pending_msg"))
            return
        self._processing = True
        self._set_secondary_buttons_enabled(False)
        self._set_glow_button_loading(self._btn_run, True, self._t("removing_short"))
        self._set_preview_loading(True, self._t("loading_remove_sub"))
        threading.Thread(target=lambda: self._process_all(targets), daemon=True).start()

    def _process_one(self, data: bytes, matting: bool, thr: int) -> Image.Image:
        src = Image.open(io.BytesIO(data)).convert("RGB")

        # Modo Sticker: flood fill remove apenas o fundo externo, sem usar IA
        if self._sticker_mode.get():
            return remover_fundo_sticker(src)

        bg_rgb = estimate_background_color(src)
        bg_brightness = float(np.mean(bg_rgb))
        artwork_mode = is_artwork_like_image(src, bg_rgb)
        erode_size, clean_threshold, edge_radius = processing_profile(src.width, src.height, thr)
        use_matting = bool(matting and not artwork_mode)

        try:
            if use_matting:
                out = rembg_remove(data,
                                   session=self._rembg_session,
                                   alpha_matting=True,
                                   alpha_matting_foreground_threshold=240,
                                   alpha_matting_background_threshold=10,
                                   alpha_matting_erode_size=erode_size)
            else:
                out = rembg_remove(data, session=self._rembg_session)
        except Exception:
            out = rembg_remove(data, session=self._rembg_session)
        img = Image.open(io.BytesIO(out)).convert("RGBA")

        # Artes/logos em fundo uniforme precisam de uma pipeline menos agressiva,
        # senão os detalhes do design acabam sendo confundidos com o fundo.
        if artwork_mode:
            img = reforcar_detalhes_de_arte(src, img, bg_rgb, distance_threshold=26.0)
            return sanitizar_rgb_transparente(img)

        img = refinar_alpha_com_fundo(
            src, img, bg_rgb,
            edge_radius=max(3, edge_radius + 1),
            low=18.0,
            high=92.0
        )
        if self._hair_protect.get() and not self._modo_simples.get():
            img = proteger_fios_de_cabelo(src, img, bg_rgb, edge_radius=max(2, edge_radius))
        sim_thr = 46.0 if bg_brightness < 170.0 else 62.0
        img = descontaminar_bordas(img, bg_rgb, edge_radius=max(2, edge_radius), similarity_threshold=sim_thr)
        if clean_threshold < 255:
            cleanup_thr = clean_threshold if bg_brightness < 170.0 else min(clean_threshold, 212)
            img = limpar_bordas(img, cleanup_thr, edge_radius=edge_radius)
        img = suavizar_borda_humana(src, img, bg_rgb, edge_radius=max(1, edge_radius))
        img = suavizar_serrilhado_alpha(img, edge_radius=max(1, edge_radius), blur_radius=0.72)
        img = sanitizar_rgb_transparente(img)

        # Filtro de cores: remove resíduos do fundo com base nas cores detectadas
        active_colors = self._get_active_removal_colors()
        if active_colors:
            img = aplicar_color_key(
                img, src, active_colors,
                tolerance=self._color_key_tol.get(),
                suppress_spill=self._spill_suppress.get()
            )
        return img

    def _process_all(self, targets):
        total = len(targets)
        self._prog.config(maximum=total)
        simples = self._modo_simples.get()
        matting = True if simples else self._alpha_mat.get()
        thr = self._thr_main.get()
        ok = 0

        for step, (idx, path, force_reprocess) in enumerate(targets):
            if self._stop_requested.is_set():
                break
            nome = Path(path).name
            self.after(0, lambda n=nome, j=step: (
                self._set_status(self._t("processing_status", current=j+1, total=total, name=n), DIM),
                self._lbl_count.config(text=f"{j}/{total}")))
            try:
                with open(path,"rb") as f: data = f.read()
                result = self._process_one(data, matting, thr)
                if self._stop_requested.is_set():
                    break
                self._results[path] = result
                if force_reprocess:
                    self._retouched.pop(path, None)
                self._reset_history(path, result)
                self._failed_files.discard(path)
                self.after(0, lambda p=path: self._style_file_row(p))
                ok += 1
            except Exception as e:
                if self._stop_requested.is_set():
                    break
                self._failed_files.add(path)
                self.after(0, lambda p=path: self._style_file_row(p))
                print(f"Error {nome}: {e}")
            self.after(0, lambda v=step+1: self._prog.config(value=v))
            if self._sel == idx:
                self.after(0, self._on_select)

        self._processing = False
        if self._stop_requested.is_set():
            return
        selected_ready = False
        if self._sel is not None and self._sel < len(self._files):
            selected_path = self._files[self._sel]
            selected_ready = selected_path in self._results or selected_path in self._retouched
        self.after(0, lambda: (
            self._set_preview_loading(False),
            self._set_status(self._t("done_status", ok=ok, total=total), SUCCESS),
            self._lbl_count.config(text=f"{total}/{total}"),
            self._set_secondary_buttons_enabled(selected_ready),
            self._set_glow_button_loading(self._btn_run, False)))

    # ── Retoque ───────────────────────────────────────────────
    def _apply_retouch(self):
        if self._sel is None:
            messagebox.showinfo(self._t("nothing_selected_title"), self._t("nothing_selected_msg")); return
        path = self._files[self._sel]
        base = self._results.get(path)
        if base is None:
            messagebox.showinfo(self._t("process_first_title"), self._t("process_first_msg")); return

        thr = self._thr_main.get()
        erode = self._erode_ret.get()
        self._set_status(self._t("refining_status"), DIM)
        self._set_secondary_buttons_enabled(False)
        self._set_preview_loading(True, self._t("loading_refine_sub"))

        def _t():
            r = limpar_bordas(base.copy(), thr)
            r = erosao_alpha(r, erode)
            try:
                original = Image.open(path).convert("RGB")
                bg_rgb = estimate_background_color(original)
                if self._hair_protect.get() and not self._modo_simples.get():
                    r = proteger_fios_de_cabelo(original, r, bg_rgb, edge_radius=2)
                r = suavizar_borda_humana(original, r, bg_rgb, edge_radius=2)
            except Exception:
                pass
            r = suavizar_serrilhado_alpha(r, edge_radius=2, blur_radius=0.9)
            r = sanitizar_rgb_transparente(r)
            if self._stop_requested.is_set():
                return
            self._retouched[path] = r
            self.after(0, lambda: (
                self._reset_history(path, r),
                self._set_preview_loading(False),
                self._set_card(self._rt_card_a, r, preserve_view=True) if self._rt_card_a else None,
                self._set_card(self._card_a, r, preserve_view=True),
                self._set_secondary_buttons_enabled(True),
                self._style_file_row(path),
                self._set_status(self._t("refining_done"), SUCCESS)))
        threading.Thread(target=_t, daemon=True).start()

    def _reprocess(self):
        if self._sel is None: return
        if not rembg_pronto: return
        path = self._files[self._sel]
        self._set_status(self._t("reprocess_status"), DIM)
        self._set_secondary_buttons_enabled(False)
        self._set_preview_loading(True, self._t("loading_reprocess_sub"))

        def _t():
            try:
                with open(path,"rb") as f: data = f.read()
                r = self._process_one(data, True, self._thr_main.get())
                if self._stop_requested.is_set():
                    return
                self._results[path] = r
                self._retouched.pop(path, None)
                self.after(0, lambda: (
                    self._reset_history(path, r),
                    self._set_preview_loading(False),
                    self._set_card(self._rt_card_b, r, preserve_view=True) if self._rt_card_b else None,
                    self._set_card(self._card_a, r, preserve_view=True),
                    self._clear_card(self._rt_card_a, self._t("refine_edges")) if self._rt_card_a else None,
                    self._set_secondary_buttons_enabled(True),
                    self._style_file_row(path),
                    self._set_status(self._t("reprocess_done"), SUCCESS)))
            except Exception as e:
                self.after(0, lambda: (
                    self._set_preview_loading(False),
                    self._set_secondary_buttons_enabled(True),
                    self._set_status(f"Error: {e}", ERROR)))
        threading.Thread(target=_t, daemon=True).start()

    # ── Salvar ────────────────────────────────────────────────
    def _save_file(self, orig: str, img: Image.Image):
        p = Path(orig)
        spec = EXPORT_FORMATS.get(self._export_format_key, EXPORT_FORMATS["png"])
        dest = (Path(self._out_dir) if self._out_dir else p.parent) / (p.stem + "_transparent" + spec["ext"])
        out_w, out_h = self._get_resize_dimensions()
        resized = resize_to_dimensions(img, out_w, out_h)
        final_img = prepare_export_image(resized, spec["transparent"])

        save_kwargs = {}
        if spec["pil_format"] == "WEBP":
            save_kwargs.update({"quality": 95, "method": 6})
        elif spec["pil_format"] == "JPEG":
            save_kwargs.update({"quality": 95, "subsampling": 0})

        final_img.save(str(dest), spec["pil_format"], **save_kwargs)
        return dest, final_img

    def _export_original_resized(self):
        """Exporta a imagem ORIGINAL redimensionada, sem remover fundo."""
        if self._sel is None or self._sel >= len(self._files):
            messagebox.showinfo(self._t("nothing_selected_title"), self._t("nothing_selected_msg"))
            return
        out_w, out_h = self._get_resize_dimensions()
        if not out_w or not out_h:
            messagebox.showinfo(
                self._t("nothing_selected_title"),
                "Enable 'Resize on export' and set width/height first."
                if self._lang == "en" else
                "Ative 'Redimensionar ao exportar' e defina largura/altura primeiro."
            )
            return
        path = self._files[self._sel]
        try:
            original = Image.open(path)
        except Exception as exc:
            messagebox.showerror("Error", str(exc))
            return

        p = Path(path)
        spec = EXPORT_FORMATS.get(self._export_format_key, EXPORT_FORMATS["png"])
        dest = (Path(self._out_dir) if self._out_dir else p.parent) / (p.stem + f"_{out_w}x{out_h}" + spec["ext"])

        resized = resize_to_dimensions(original.convert("RGBA" if spec["transparent"] else "RGB"), out_w, out_h)
        final_img = prepare_export_image(resized, spec["transparent"])

        save_kwargs = {}
        if spec["pil_format"] == "WEBP":
            save_kwargs.update({"quality": 95, "method": 6})
        elif spec["pil_format"] == "JPEG":
            save_kwargs.update({"quality": 95, "subsampling": 0})

        final_img.save(str(dest), spec["pil_format"], **save_kwargs)
        self._set_status(
            self._t("exported_status", name=dest.name,
                    size=f"{final_img.width}×{final_img.height}px",
                    folder=dest.parent),
            SUCCESS
        )

    def _export_current(self):
        if self._sel is None: return
        path = self._files[self._sel]
        img = self._retouched.get(path) or self._results.get(path)
        if not img: return
        dest, final_img = self._save_file(path, img)
        self._set_status(
            self._t(
                "exported_status",
                name=dest.name,
                size=f"{final_img.width}×{final_img.height}px",
                folder=dest.parent,
            ),
            SUCCESS
        )

    def _copy_current_to_clipboard(self):
        if self._sel is None:
            messagebox.showinfo(self._t("nothing_selected_title"), self._t("nothing_selected_msg"))
            return

        path = self._files[self._sel]
        img = self._retouched.get(path) or self._results.get(path)
        if not img:
            messagebox.showinfo(self._t("process_first_title"), self._t("process_first_msg"))
            return

        try:
            copy_image_to_clipboard(img)
            self._set_status(self._t("copied_status"), SUCCESS)
        except Exception:
            messagebox.showerror(self._t("clipboard_error_title"), self._t("clipboard_error_msg"))

    def _save_current(self):
        self._export_current()

    def _save_retouched(self):
        if self._sel is None: return
        path = self._files[self._sel]
        img = self._retouched.get(path)
        if not img:
            messagebox.showinfo(self._t("refine_first_title"), self._t("refine_first_msg")); return
        dest, _final_img = self._save_file(path, img)
        self._set_status(self._t("refined_exported_status", folder=dest.parent), SUCCESS)


if __name__ == "__main__":
    app = App()
    app.mainloop()
