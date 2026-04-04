# -*- mode: python ; coding: utf-8 -*-
# Background Remover Studio — PyInstaller spec (onedir)
#
# Build: build.bat  or  pyinstaller main.spec --noconfirm --clean
# Output: dist/BackgroundRemoverStudio/BackgroundRemoverStudio.exe
#
# onedir mode keeps onnxruntime DLLs happy. UPX disabled for same reason.
# AI model (~170 MB) is NOT bundled — rembg downloads it on first run.

from PyInstaller.utils.hooks import collect_all

datas_rembg,  bins_rembg,  hid_rembg  = collect_all("rembg")
datas_ort,    bins_ort,    hid_ort    = collect_all("onnxruntime")
datas_pymat,  bins_pymat,  hid_pymat  = collect_all("pymatting")
datas_pooch,  bins_pooch,  hid_pooch  = collect_all("pooch")

try:
    datas_ski, bins_ski, hid_ski = collect_all("skimage")
except Exception:
    datas_ski = bins_ski = hid_ski = []

app_datas = [
    ("src/icon.ico", "."),
]

all_datas    = app_datas + datas_rembg + datas_ort + datas_pymat + datas_pooch + datas_ski
all_binaries = bins_rembg + bins_ort + bins_pymat + bins_pooch + bins_ski
all_hidden   = (
    hid_rembg + hid_ort + hid_pymat + hid_pooch + hid_ski
    + [
        "tkinter", "tkinter.ttk", "tkinter.messagebox",
        "tkinter.filedialog", "tkinter.scrolledtext", "tkinterdnd2",
        "PIL", "PIL._imaging", "PIL.Image", "PIL.ImageFilter",
        "PIL.ImageDraw", "PIL.ImageTk", "PIL.ImageFont",
        "numpy", "numpy.core",
        "scipy", "scipy.special", "scipy.special._ufuncs",
        "scipy.linalg", "scipy.ndimage",
        "urllib.request", "urllib.parse",
        "json", "threading", "subprocess",
        "ctypes", "ctypes.wintypes",
        "platformdirs", "requests", "tqdm", "tqdm.auto",
    ]
)

a = Analysis(
    ["src/main.py"],
    pathex=["src"],
    binaries=all_binaries,
    datas=all_datas,
    hiddenimports=all_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib", "IPython", "jupyter", "notebook",
        "sphinx", "pytest", "xmlrpc", "email.mime", "html", "http.server",
    ],
    noarchive=False,
    optimize=1,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="BackgroundRemoverStudio",
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
    version="version_info.txt",
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name="BackgroundRemoverStudio",
)
