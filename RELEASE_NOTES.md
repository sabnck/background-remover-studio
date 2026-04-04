# v1.1.0

## What changed

**Windows installer**
The `.bat` launcher is gone. The app now ships as `start.exe` — a proper executable that opens the setup assistant directly. No more Windows security warnings blocking the entry point.

For devs or anyone who wants to skip the installer, there's also a portable zip with the full standalone build.

**REST API**
`/api/remove-background` now accepts base64 JSON input in addition to file uploads, and can return a JSON response with the result and metadata. Useful for scripting and tool integrations.

**AI tool integrations**
`tools/` has ready-to-use definitions for ChatGPT Custom Actions and Claude function calling. Point them at a local tunnel (ngrok etc.) and the background removal is available directly inside the chat.

**Author metadata**
Exe properties (right-click → Details) now show OportuniPT as the publisher.

## Does it work on Linux?

Running from source — yes. Install the requirements and run `python src/main.py`. rembg, Pillow, and Tkinter all work on Linux.

The `start.exe` launcher and the setup assistant GUI are Windows-only for now. Linux users need to manage dependencies manually via pip. A Linux launcher is something for a future version.

## Download

| File | |
|---|---|
| `start.exe` | Opens setup assistant — install, launch, repair from one place |
| `BackgroundRemoverStudio-portable.zip` | Standalone build, no installation needed |

AI model (~170 MB) downloads on first use. Everything else works offline.

## Changelog

- `start.exe` — replaces start.bat, compiled with PyInstaller, no SAC warnings
- `src/launcher.py` — source for start.exe, finds Python and opens setup_assistant
- `src/api_server.py` — base64 input, JSON response mode, CORS, `/api/info`, OpenAPI at `/api/docs`
- `src/_paths.py` — resource path helper, works correctly inside frozen bundles
- `tools/` — openapi_action.yaml, claude_tool.json, chatgpt_action.json
- `main.spec` — onedir build, full ML dependency collection, version metadata
- `build.bat` — builds both main app and start.exe, Inno Setup fallback to portable zip
- `version_info.txt` / `version_info_launcher.txt` — Windows exe metadata (OportuniPT, Henrique Fernandes)
