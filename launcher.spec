# -*- mode: python ; coding: utf-8 -*-
# Background Remover Studio — launcher spec
# Compiles src/launcher.py into start.exe (small, onefile, no console window).
# Built automatically by build.bat.

a = Analysis(
    ["src/launcher.py"],
    pathex=["src"],
    binaries=[],
    datas=[],
    hiddenimports=["tkinter", "tkinter.messagebox"],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "numpy", "PIL", "rembg", "onnxruntime", "scipy",
        "fastapi", "uvicorn", "starlette",
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name="start",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="src/icon.ico",
    version="version_info_launcher.txt",
)
