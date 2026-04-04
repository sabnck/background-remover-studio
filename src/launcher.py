"""
Background Remover Studio — launcher.
Finds Python on the system and opens the setup assistant.
Compiled to start.exe by build.bat (PyInstaller onefile, no console).
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _find_python() -> str | None:
    """Return path to pythonw.exe (or python.exe) on the user's system."""
    candidates: list[str] = []

    # 1. py launcher
    try:
        r = subprocess.run(
            ["py", "-3", "-c", "import sys; print(sys.executable)"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode == 0:
            candidates.append(r.stdout.strip())
    except Exception:
        pass

    # 2. python / pythonw in PATH
    for name in ("pythonw", "python"):
        try:
            r = subprocess.run(
                ["where", name], capture_output=True, text=True, timeout=5,
            )
            if r.returncode == 0:
                for line in r.stdout.splitlines():
                    p = line.strip()
                    if p:
                        candidates.append(p)
        except Exception:
            pass

    # 3. Common install locations (LocalAppData and Program Files)
    import os
    search_roots = [
        Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Python",
        Path(os.environ.get("PROGRAMFILES", "")) ,
        Path(os.environ.get("PROGRAMFILES(X86)", "")),
    ]
    for root in search_roots:
        if not root.exists():
            continue
        for exe_name in ("pythonw.exe", "python.exe"):
            for match in sorted(root.rglob(exe_name), reverse=True):
                candidates.append(str(match))

    # Return the first candidate that actually runs Python 3.10+
    for candidate in candidates:
        p = Path(candidate)
        if not p.exists():
            continue
        try:
            r = subprocess.run(
                [str(p), "-c", "import sys; sys.exit(0 if sys.version_info>=(3,10) else 1)"],
                capture_output=True, timeout=5,
            )
            if r.returncode == 0:
                # Prefer pythonw (no console flash)
                pythonw = p.with_name("pythonw.exe")
                return str(pythonw) if pythonw.exists() else str(p)
        except Exception:
            continue
    return None


def _show_error(msg: str) -> None:
    try:
        import tkinter as tk
        from tkinter import messagebox
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("Background Remover Studio", msg)
        root.destroy()
    except Exception:
        pass


def main() -> None:
    # The launcher lives in the project root → src/ is next to it
    if getattr(sys, "frozen", False):
        root_dir = Path(sys.executable).parent
    else:
        root_dir = Path(__file__).resolve().parent.parent

    assistant = root_dir / "src" / "setup_assistant.pyw"

    if not assistant.exists():
        _show_error(
            f"Could not find setup_assistant.pyw.\n"
            f"Expected at: {assistant}\n\n"
            "Make sure the launcher is in the same folder as the src/ directory."
        )
        return

    python = _find_python()
    if not python:
        _show_error(
            "Python 3.10 or newer was not found on this machine.\n\n"
            "Download and install Python from:\nhttps://www.python.org/downloads/\n\n"
            "Make sure to check 'Add Python to PATH' during installation."
        )
        return

    subprocess.Popen(
        [python, str(assistant)],
        cwd=str(assistant.parent),
    )


if __name__ == "__main__":
    main()
