"""Resource path helper — works in dev and PyInstaller onedir bundles.

Usage:
    from _paths import resource, app_root

    icon_path = resource("icon.ico")
    web_dir   = resource("webui")
"""

from __future__ import annotations

import sys
from pathlib import Path


def app_root() -> Path:
    """Return the application root directory.

    - PyInstaller onedir bundle: directory containing the .exe
    - Development: src/ directory (parent of this file)
    """
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    return Path(__file__).parent


def resource(relative: str) -> Path:
    """Return an absolute path to a bundled resource file or folder."""
    return app_root() / relative
