from __future__ import annotations

import importlib.util
import locale
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, scrolledtext

APP_DIR = Path(__file__).resolve().parent
MAIN_FILE = APP_DIR / "main.py"
ICON_FILE = APP_DIR / "icon.ico"
MODEL_CACHE_DIR = Path.home() / ".u2net"
ROOT_DIR = APP_DIR.parent
LOCAL_CLEAN_TARGETS = [
    APP_DIR / "__pycache__",
    APP_DIR / "Background Remover Studio.lnk",
    APP_DIR / "Start.lnk",
    ROOT_DIR / "Background Remover Studio.lnk",  # shortcut auto-created on first run
]
REQUIRED_MODULES = {"rembg": "rembg[cpu]", "PIL": "pillow", "numpy": "numpy", "tkinterdnd2": "tkinterdnd2"}
INSTALL_PACKAGES = ["rembg[cpu]", "pillow", "numpy", "tkinterdnd2"]
UNINSTALL_PACKAGES = ["rembg", "pillow", "numpy", "tkinterdnd2", "onnxruntime", "pymatting", "pooch"]

BG = "#0B0F14"
CARD = "#111827"
CARD_ALT = "#161D28"
BORDER = "#222B38"
TEXT = "#F7F9FC"
DIM = "#9CA7B5"
MUTED = "#6E7888"
ACCENT = "#3994FF"
ACCENT_HOVER = "#5AA7FF"
SUCCESS = "#3DD68C"
WARNING = "#E8BC72"

TXT = {
    "en": {
        "title": "Background Remover Studio Setup",
        "subtitle": "Launch, install dependencies, or clean up the app with a safer guided flow.",
        "env": "Environment",
        "notes": "What this assistant does",
        "bullets": [
            "Checks the current Python environment.",
            "Installs only the packages required by this app.",
            "Offers a cleanup flow before removing anything.",
            "Never touches your source images or exported artwork.",
        ],
        "open": "Open App",
        "launch_pick_title": "Open Background Remover Studio",
        "launch_pick_sub": "Choose how you want to launch the app.",
        "launch_desktop": "Desktop App",
        "launch_desktop_sub": "Native app — works fully offline.",
        "launch_web": "Web UI",
        "launch_web_sub": "Open in your browser.",
        "launch_soon": "Coming soon",
        "install": "Install / Repair Dependencies",
        "install_only": "Install Dependencies",
        "uninstall": "Uninstall / Cleanup",
        "refresh": "Refresh Status",
        "activity": "Activity",
        "assistant_ready": "Assistant ready.",
        "status_checking": "Checking dependencies...",
        "status_ready": "Everything looks ready.",
        "status_missing": "Action needed: dependencies are missing.",
        "python_env": "Python environment:\n{path}",
        "deps_missing": "Missing packages:\n{packages}",
        "deps_installed": "Dependencies installed:\nrembg[cpu], pillow, numpy, tkinterdnd2",
        "deps_missing_title": "Dependencies missing",
        "deps_missing_msg": "Install the required dependencies before opening the app.",
        "launch_error_title": "Launch error",
        "launch_error_msg": "Unable to open the app.\n\n{error}",
        "install_title": "Install dependencies",
        "install_summary": "This will install or repair the dependencies required by Background Remover Studio\nin the current Python environment:\n\n- rembg[cpu]\n- pillow\n- numpy\n- tkinterdnd2\n\nContinue?",
        "install_busy": "Installing dependencies...",
        "install_done": "Installation completed.",
        "install_failed": "Installation failed.",
        "install_ok_title": "Ready",
        "install_ok_msg": "Dependencies installed successfully.",
        "install_fail_title": "Install error",
        "install_fail_msg": "Failed to install dependencies.",
        "dlg_title": "Uninstall / Cleanup",
        "dlg_sub": "Choose what should be removed. Your personal images and exported files will never be touched.",
        "local_title": "Remove local generated files",
        "local_sub": "__pycache__ and launcher shortcuts in this folder",
        "pkg_title": "Remove Python packages",
        "pkg_sub": "Uninstalls packages from the current Python environment used by this app",
        "cache_title": "Remove downloaded AI model cache",
        "cache_sub": "Deletes {path}",
        "dlg_note": "Note: if you want a full portable uninstall, delete this project folder manually after cleanup.",
        "cancel": "Cancel",
        "continue": "Continue",
        "nothing_title": "Nothing selected",
        "nothing_msg": "Select at least one cleanup option.",
        "confirm_title": "Confirm cleanup",
        "confirm_msg": "The following items will be removed:\n\n{summary}\n\nContinue?",
        "cleanup_busy": "Running cleanup...",
        "cleanup_done": "Cleanup completed.",
        "cleanup_done_title": "Finished",
        "cleanup_done_msg": "Cleanup finished.\nYou can delete the app folder manually if you no longer need it.",
        "summary_local": "local generated files in this folder",
        "summary_pkg": "Python packages from the current environment",
        "summary_cache": "downloaded AI model cache",
    },
    "pt": {
        "title": "Background Remover Studio Setup",
        "subtitle": "Abra o app, instale dependências ou limpe a instalação com um fluxo mais seguro.",
        "env": "Ambiente",
        "notes": "O que este assistente faz",
        "bullets": [
            "Verifica o ambiente Python atual.",
            "Instala apenas os pacotes necessários para este app.",
            "Mostra um fluxo de limpeza antes de remover qualquer coisa.",
            "Nunca toca nas suas imagens de origem nem nos ficheiros exportados.",
        ],
        "open": "Abrir App",
        "launch_pick_title": "Abrir Background Remover Studio",
        "launch_pick_sub": "Escolha como deseja executar o app.",
        "launch_desktop": "App Desktop",
        "launch_desktop_sub": "App nativo — funciona totalmente offline.",
        "launch_web": "Web UI",
        "launch_web_sub": "Abrir no navegador.",
        "launch_soon": "Em breve",
        "install": "Instalar / Reparar Dependências",
        "install_only": "Instalar Dependências",
        "uninstall": "Desinstalar / Limpar",
        "refresh": "Atualizar Estado",
        "activity": "Atividade",
        "assistant_ready": "Assistente pronto.",
        "status_checking": "A verificar dependências...",
        "status_ready": "Está tudo pronto.",
        "status_missing": "Atenção: faltam dependências.",
        "python_env": "Ambiente Python:\n{path}",
        "deps_missing": "Pacotes em falta:\n{packages}",
        "deps_installed": "Dependências instaladas:\nrembg[cpu], pillow, numpy, tkinterdnd2",
        "deps_missing_title": "Dependências em falta",
        "deps_missing_msg": "Instale as dependências necessárias antes de abrir o app.",
        "launch_error_title": "Erro ao abrir",
        "launch_error_msg": "Não foi possível abrir o app.\n\n{error}",
        "install_title": "Instalar dependências",
        "install_summary": "Isto vai instalar ou reparar as dependências necessárias para o Background Remover Studio\nno ambiente Python atual:\n\n- rembg[cpu]\n- pillow\n- numpy\n- tkinterdnd2\n\nContinuar?",
        "install_busy": "A instalar dependências...",
        "install_done": "Instalação concluída.",
        "install_failed": "A instalação falhou.",
        "install_ok_title": "Pronto",
        "install_ok_msg": "Dependências instaladas com sucesso.",
        "install_fail_title": "Erro de instalação",
        "install_fail_msg": "Falha ao instalar as dependências.",
        "dlg_title": "Desinstalar / Limpar",
        "dlg_sub": "Escolha o que deve ser removido. As suas imagens e exportações nunca serão tocadas.",
        "local_title": "Remover ficheiros gerados localmente",
        "local_sub": "__pycache__ e atalhos do launcher nesta pasta",
        "pkg_title": "Remover pacotes Python",
        "pkg_sub": "Desinstala pacotes do ambiente Python atual usado por este app",
        "cache_title": "Remover cache do modelo de IA",
        "cache_sub": "Apaga {path}",
        "dlg_note": "Nota: se quiser uma desinstalação totalmente portátil, apague esta pasta manualmente depois da limpeza.",
        "cancel": "Cancelar",
        "continue": "Continuar",
        "nothing_title": "Nada selecionado",
        "nothing_msg": "Selecione pelo menos uma opção de limpeza.",
        "confirm_title": "Confirmar limpeza",
        "confirm_msg": "Os seguintes itens serão removidos:\n\n{summary}\n\nContinuar?",
        "cleanup_busy": "A executar limpeza...",
        "cleanup_done": "Limpeza concluída.",
        "cleanup_done_title": "Concluído",
        "cleanup_done_msg": "Limpeza concluída.\nPode apagar manualmente a pasta do app se já não precisar dela.",
        "summary_local": "ficheiros gerados localmente nesta pasta",
        "summary_pkg": "pacotes Python do ambiente atual",
        "summary_cache": "cache do modelo de IA transferido",
    },
}


def detect_language() -> str:
    try:
        lang = (locale.getdefaultlocale()[0] or "").lower()
    except Exception:
        lang = ""
    return "pt" if lang.startswith("pt") else "en"


def python_cli_executable() -> str:
    current = Path(sys.executable)
    if current.name.lower() == "pythonw.exe":
        candidate = current.with_name("python.exe")
        if candidate.exists():
            return str(candidate)
    return str(current)


def python_gui_executable() -> str:
    current = Path(sys.executable)
    if current.name.lower() == "python.exe":
        candidate = current.with_name("pythonw.exe")
        if candidate.exists():
            return str(candidate)
    return str(current)


def creation_flags() -> int:
    return getattr(subprocess, "CREATE_NO_WINDOW", 0)


class Assistant(tk.Tk):
    def __init__(self, uninstall_only: bool = False):
        super().__init__()
        self.uninstall_only = uninstall_only
        self._lang = detect_language()
        self._busy = False
        self._missing_modules: list[str] = []
        self._status_key = "status_checking"
        self._status_color = DIM
        self.title(self.t("title"))
        self.configure(bg=BG)
        self.geometry("760x600")
        self.minsize(720, 560)
        self._center()
        if ICON_FILE.exists():
            try:
                self.iconbitmap(str(ICON_FILE))
            except Exception:
                pass
        self._build()
        self.after(80, self.refresh_state)
        self.after(600, self._create_root_shortcut)
        if self.uninstall_only:
            self.after(180, self.open_uninstall_dialog)

    def _create_root_shortcut(self) -> None:
        """Create a shortcut with the app icon in the root folder (runs silently once)."""
        lnk = ROOT_DIR / "Background Remover Studio.lnk"
        if lnk.exists():
            return
        try:
            pyw = python_gui_executable()
            script = str(Path(__file__).resolve())
            icon = str(ICON_FILE)
            work = str(APP_DIR)
            ps = (
                f'$s=(New-Object -COM WScript.Shell).CreateShortcut("{lnk}");'
                f'$s.TargetPath="{pyw}";'
                f'$s.Arguments=\'"{script}"\';'
                f'$s.IconLocation="{icon}, 0";'
                f'$s.Description="Background Remover Studio";'
                f'$s.WorkingDirectory="{work}";'
                f'$s.Save()'
            )
            subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
                capture_output=True,
                creationflags=creation_flags(),
                timeout=10,
            )
        except Exception:
            pass  # Non-critical: shortcut creation is a convenience feature

    def t(self, key: str, **kwargs) -> str:
        value = TXT[self._lang][key]
        return value.format(**kwargs) if kwargs else value

    def _center(self):
        self.update_idletasks()
        w, h = self.winfo_width(), self.winfo_height()
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        self.geometry(f"+{(sw - w) // 2}+{(sh - h) // 2}")

    def _center_window(self, window: tk.Toplevel):
        window.update_idletasks()
        w, h = window.winfo_width(), window.winfo_height()
        sw, sh = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry(f"+{max(30, (sw - w) // 2)}+{max(30, (sh - h) // 2)}")

    def _build(self):
        outer = tk.Frame(self, bg=BG, padx=18, pady=18)
        outer.pack(fill="both", expand=True)
        outer.columnconfigure(0, weight=1)
        outer.rowconfigure(3, weight=1)

        header = tk.Frame(outer, bg=CARD, padx=22, pady=18, highlightthickness=1, highlightbackground=BORDER)
        header.grid(row=0, column=0, sticky="ew")
        header.columnconfigure(0, weight=1)
        title_wrap = tk.Frame(header, bg=CARD)
        title_wrap.grid(row=0, column=0, sticky="w")
        self.lbl_title = tk.Label(title_wrap, bg=CARD, fg=TEXT, font=("Segoe UI", 22, "bold"))
        self.lbl_title.pack(anchor="w")
        self.lbl_subtitle = tk.Label(title_wrap, bg=CARD, fg=DIM, font=("Segoe UI", 10))
        self.lbl_subtitle.pack(anchor="w", pady=(6, 0))
        lang_wrap = tk.Frame(header, bg=CARD, padx=10, pady=8, highlightthickness=1, highlightbackground=BORDER)
        lang_wrap.grid(row=0, column=1, sticky="e")
        self.btn_lang_en = self._button(lang_wrap, "EN", lambda: self.set_language("en"), small=True)
        self.btn_lang_en.pack(side="left")
        tk.Label(lang_wrap, text="|", bg=CARD, fg=MUTED, font=("Segoe UI", 9)).pack(side="left", padx=6)
        self.btn_lang_pt = self._button(lang_wrap, "PTBR", lambda: self.set_language("pt"), small=True)
        self.btn_lang_pt.pack(side="left")

        info = tk.Frame(outer, bg=BG)
        info.grid(row=1, column=0, sticky="ew", pady=(14, 14))
        info.columnconfigure(0, weight=1)
        info.columnconfigure(1, weight=1)
        left = tk.Frame(info, bg=CARD_ALT, padx=18, pady=16, highlightthickness=1, highlightbackground=BORDER)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        right = tk.Frame(info, bg=CARD_ALT, padx=18, pady=16, highlightthickness=1, highlightbackground=BORDER)
        right.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        self.lbl_env = tk.Label(left, bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 12, "bold"))
        self.lbl_env.pack(anchor="w")
        self.lbl_status = tk.Label(left, bg=CARD_ALT, fg=DIM, font=("Segoe UI", 10), justify="left", wraplength=300)
        self.lbl_status.pack(anchor="w", pady=(10, 4))
        self.lbl_python = tk.Label(left, bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 9), justify="left", wraplength=300)
        self.lbl_python.pack(anchor="w")
        self.lbl_deps = tk.Label(left, bg=CARD_ALT, fg=MUTED, font=("Segoe UI", 9), justify="left", wraplength=300)
        self.lbl_deps.pack(anchor="w", pady=(6, 0))
        self.lbl_notes = tk.Label(right, bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 12, "bold"))
        self.lbl_notes.pack(anchor="w")
        self.note_labels = []
        for _ in range(4):
            lbl = tk.Label(right, bg=CARD_ALT, fg=DIM, font=("Segoe UI", 9), justify="left", anchor="w", wraplength=300)
            lbl.pack(anchor="w", pady=(8, 0))
            self.note_labels.append(lbl)

        actions = tk.Frame(outer, bg=CARD, padx=18, pady=18, highlightthickness=1, highlightbackground=BORDER)
        actions.grid(row=2, column=0, sticky="ew")
        actions.columnconfigure(0, weight=1)
        actions.columnconfigure(1, weight=1)
        self.btn_open = self._button(actions, "", self.open_app, primary=True)
        self.btn_open.grid(row=0, column=0, sticky="ew", padx=(0, 8))
        self.btn_install = self._button(actions, "", self.install_requirements)
        self.btn_install.grid(row=0, column=1, sticky="ew", padx=(8, 0))
        self.btn_uninstall = self._button(actions, "", self.open_uninstall_dialog)
        self.btn_uninstall.grid(row=1, column=0, sticky="ew", padx=(0, 8), pady=(12, 0))
        self.btn_refresh = self._button(actions, "", lambda: self.refresh_state(False))
        self.btn_refresh.grid(row=1, column=1, sticky="ew", padx=(8, 0), pady=(12, 0))

        log_card = tk.Frame(outer, bg=CARD, padx=18, pady=18, highlightthickness=1, highlightbackground=BORDER)
        log_card.grid(row=3, column=0, sticky="nsew", pady=(14, 0))
        log_card.columnconfigure(0, weight=1)
        log_card.rowconfigure(1, weight=1)
        self.lbl_activity = tk.Label(log_card, bg=CARD, fg=TEXT, font=("Segoe UI", 12, "bold"))
        self.lbl_activity.grid(row=0, column=0, sticky="w")
        self.log = scrolledtext.ScrolledText(log_card, bg="#0E131A", fg="#D7E3F0", insertbackground=TEXT, font=("Consolas", 9), relief="flat", bd=0, wrap="word", height=12)
        self.log.grid(row=1, column=0, sticky="nsew", pady=(12, 0))
        self.apply_texts(initial=True)

    def _button(self, parent, text, command, primary=False, small=False):
        btn = tk.Button(parent, text=text, command=command, bg=ACCENT if primary else CARD_ALT, fg="#08131F" if primary else TEXT,
                        activebackground=ACCENT_HOVER if primary else "#202938", activeforeground="#08131F" if primary else TEXT,
                        highlightthickness=1, highlightbackground=BORDER, highlightcolor=BORDER, relief="flat", bd=0,
                        font=("Segoe UI", 9 if small else 10, "bold"), padx=10 if small else 12, pady=5 if small else 11, cursor="hand2")
        return btn

    def apply_texts(self, initial=False):
        self.title(self.t("title"))
        self.lbl_title.config(text=self.t("title"))
        self.lbl_subtitle.config(text=self.t("subtitle"), wraplength=520)
        self.lbl_env.config(text=self.t("env"))
        self.lbl_notes.config(text=self.t("notes"))
        for lbl, line in zip(self.note_labels, self.t("bullets")):
            lbl.config(text=f"- {line}")
        self.lbl_activity.config(text=self.t("activity"))
        self.btn_open.config(text=self.t("open"))
        self.btn_install.config(text=self.t("install") if not self._missing_modules else self.t("install_only"))
        self.btn_uninstall.config(text=self.t("uninstall"))
        self.btn_refresh.config(text=self.t("refresh"))
        active_bg = "#243754"
        inactive = CARD_ALT
        self.btn_lang_en.config(text="EN", bg=active_bg if self._lang == "en" else inactive)
        self.btn_lang_pt.config(text="PTBR", bg=active_bg if self._lang == "pt" else inactive)
        if initial:
            self.log.configure(state="normal")
            self.log.delete("1.0", "end")
            self.log.insert("end", self.t("assistant_ready") + "\n")
            self.log.configure(state="disabled")
        self.lbl_status.config(text=self.t(self._status_key), fg=self._status_color)

    def set_language(self, lang):
        if lang == self._lang:
            return
        self._lang = lang
        self.apply_texts()
        self.refresh_state(silent=True)

    def _log(self, text):
        self.log.configure(state="normal")
        self.log.insert("end", text.rstrip() + "\n")
        self.log.see("end")
        self.log.configure(state="disabled")

    def _set_busy(self, busy, status_key=None):
        self._busy = busy
        for btn in (self.btn_open, self.btn_install, self.btn_uninstall, self.btn_refresh):
            btn.config(state="disabled" if busy else "normal")
        if status_key:
            self._status_key = status_key
            self._status_color = WARNING if busy else DIM
            self.lbl_status.config(text=self.t(status_key), fg=self._status_color)

    def missing_modules(self):
        return [name for name in REQUIRED_MODULES if importlib.util.find_spec(name) is None]

    def refresh_state(self, silent=False):
        if self._busy:
            return
        self._missing_modules = self.missing_modules()
        self.lbl_python.config(text=self.t("python_env", path=python_cli_executable()))
        if self._missing_modules:
            packages = ", ".join(REQUIRED_MODULES[name] for name in self._missing_modules)
            self._status_key = "status_missing"
            self._status_color = WARNING
            self.lbl_status.config(text=self.t("status_missing"), fg=WARNING)
            self.lbl_deps.config(text=self.t("deps_missing", packages=packages))
            self.btn_open.config(state="disabled")
            self.btn_install.config(text=self.t("install_only"))
            if not silent:
                self._log(self.t("deps_missing", packages=packages))
        else:
            self._status_key = "status_ready"
            self._status_color = SUCCESS
            self.lbl_status.config(text=self.t("status_ready"), fg=SUCCESS)
            self.lbl_deps.config(text=self.t("deps_installed"))
            self.btn_open.config(state="normal")
            self.btn_install.config(text=self.t("install"))
            if not silent:
                self._log(self.t("status_ready"))

    def open_app(self):
        if self._busy:
            return
        if self.missing_modules():
            messagebox.showwarning(self.t("deps_missing_title"), self.t("deps_missing_msg"), parent=self)
            return
        self._show_launch_picker()

    def _show_launch_picker(self):
        dialog = tk.Toplevel(self)
        dialog.title(self.t("launch_pick_title"))
        dialog.configure(bg=BG)
        dialog.transient(self)
        dialog.grab_set()
        dialog.resizable(False, False)
        if ICON_FILE.exists():
            try:
                dialog.iconbitmap(str(ICON_FILE))
            except Exception:
                pass

        wrap = tk.Frame(dialog, bg=BG, padx=24, pady=22)
        wrap.pack(fill="both", expand=True)

        # ── Header ────────────────────────────────────────────────────────────
        tk.Label(wrap, text=self.t("launch_pick_title"),
                 bg=BG, fg=TEXT, font=("Segoe UI", 15, "bold")).pack(anchor="w")
        tk.Label(wrap, text=self.t("launch_pick_sub"),
                 bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(anchor="w", pady=(4, 18))

        # ── Cards row ─────────────────────────────────────────────────────────
        row = tk.Frame(wrap, bg=BG)
        row.pack(fill="x")
        row.columnconfigure(0, weight=1)
        row.columnconfigure(1, weight=1)

        # — Desktop card (active) ——————————————
        desktop = tk.Frame(row, bg=CARD_ALT, padx=20, pady=20,
                           highlightthickness=2, highlightbackground=ACCENT,
                           cursor="hand2")
        desktop.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        tk.Label(desktop, text=self.t("launch_desktop"),
                 bg=CARD_ALT, fg=TEXT, font=("Segoe UI", 12, "bold"),
                 cursor="hand2").pack(anchor="w")
        tk.Label(desktop, text=self.t("launch_desktop_sub"),
                 bg=CARD_ALT, fg=DIM, font=("Segoe UI", 9), justify="left",
                 wraplength=160, cursor="hand2").pack(anchor="w", pady=(6, 0))

        # hover effect helpers
        def _card_enter(e, card=desktop, children=None):
            card.config(bg="#1A2535", highlightbackground=ACCENT_HOVER)
            for w in card.winfo_children():
                try:
                    w.config(bg="#1A2535")
                except Exception:
                    pass

        def _card_leave(e, card=desktop):
            card.config(bg=CARD_ALT, highlightbackground=ACCENT)
            for w in card.winfo_children():
                try:
                    w.config(bg=CARD_ALT)
                except Exception:
                    pass

        def _do_launch(dlg=dialog):
            dlg.destroy()
            try:
                subprocess.Popen(
                    [python_gui_executable(), str(MAIN_FILE)],
                    cwd=str(APP_DIR),
                    creationflags=creation_flags(),
                )
            except Exception as exc:
                messagebox.showerror(
                    self.t("launch_error_title"),
                    self.t("launch_error_msg", error=exc),
                    parent=self,
                )
                self._log(self.t("launch_error_msg", error=exc))
                return
            self._log(self.t("open"))
            self.destroy()

        desktop.bind("<Enter>", _card_enter)
        desktop.bind("<Leave>", _card_leave)
        desktop.bind("<Button-1>", lambda e: _do_launch())
        for w in desktop.winfo_children():
            w.bind("<Enter>", _card_enter)
            w.bind("<Leave>", _card_leave)
            w.bind("<Button-1>", lambda e: _do_launch())

        # — Web UI card (coming soon) ————————————————————————
        DIMMED_BG = "#0D1117"
        web = tk.Frame(row, bg=DIMMED_BG, padx=20, pady=20,
                       highlightthickness=2, highlightbackground=BORDER)
        web.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        tk.Label(web, text=self.t("launch_web"),
                 bg=DIMMED_BG, fg=MUTED, font=("Segoe UI", 12, "bold")).pack(anchor="w")
        tk.Label(web, text=self.t("launch_web_sub"),
                 bg=DIMMED_BG, fg="#455060", font=("Segoe UI", 9), justify="left",
                 wraplength=160).pack(anchor="w", pady=(6, 0))
        badge = tk.Label(web, text=f"  {self.t('launch_soon')}  ",
                         bg="#1C2330", fg=WARNING, font=("Segoe UI", 8, "bold"),
                         padx=0, pady=3,
                         highlightthickness=1, highlightbackground="#2A3445")
        badge.pack(anchor="w", pady=(12, 0))

        # ── Cancel button ─────────────────────────────────────────────────────
        footer = tk.Frame(wrap, bg=BG)
        footer.pack(fill="x", pady=(20, 0))
        tk.Button(footer, text=self.t("cancel"), command=dialog.destroy,
                  bg=CARD_ALT, fg=DIM,
                  activebackground="#202938", activeforeground=TEXT,
                  highlightthickness=1, highlightbackground=BORDER,
                  relief="flat", bd=0,
                  font=("Segoe UI", 9, "bold"), padx=14, pady=7,
                  cursor="hand2").pack(side="right")

        dialog.update_idletasks()
        self._center_window(dialog)

    def install_requirements(self):
        if self._busy:
            return
        if not messagebox.askyesno(self.t("install_title"), self.t("install_summary"), parent=self):
            return

        def worker():
            self.after(0, lambda: self._set_busy(True, "install_busy"))
            self.after(0, lambda: self._log(self.t("install_busy")))
            cmd = [python_cli_executable(), "-m", "pip", "install", "--disable-pip-version-check", *INSTALL_PACKAGES]
            try:
                proc = subprocess.Popen(cmd, cwd=str(APP_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=creation_flags())
                assert proc.stdout is not None
                for line in proc.stdout:
                    self.after(0, lambda text=line: self._log(text))
                code = proc.wait()
            except Exception as exc:
                self.after(0, lambda: self._set_busy(False, "install_failed"))
                self.after(0, lambda: messagebox.showerror(self.t("install_fail_title"), str(exc), parent=self))
                return
            if code == 0:
                self.after(0, lambda: self._set_busy(False, "install_done"))
                self.after(0, lambda: self.refresh_state(silent=True))
                self.after(0, lambda: messagebox.showinfo(self.t("install_ok_title"), self.t("install_ok_msg"), parent=self))
            else:
                self.after(0, lambda: self._set_busy(False, "install_failed"))
                self.after(0, lambda: messagebox.showerror(self.t("install_fail_title"), self.t("install_fail_msg"), parent=self))

        threading.Thread(target=worker, daemon=True).start()

    def open_uninstall_dialog(self):
        if self._busy:
            return
        dialog = tk.Toplevel(self)
        dialog.title(self.t("dlg_title"))
        dialog.configure(bg=BG)
        dialog.transient(self)
        dialog.grab_set()
        dialog.geometry("560x520")
        dialog.minsize(540, 500)
        if ICON_FILE.exists():
            try:
                dialog.iconbitmap(str(ICON_FILE))
            except Exception:
                pass
        card = tk.Frame(dialog, bg=CARD, padx=18, pady=18, highlightthickness=1, highlightbackground=BORDER)
        card.pack(fill="both", expand=True, padx=18, pady=18)
        tk.Label(card, text=self.t("dlg_title"), bg=CARD, fg=TEXT, font=("Segoe UI", 18, "bold")).pack(anchor="w")
        tk.Label(card, text=self.t("dlg_sub"), bg=CARD, fg=DIM, font=("Segoe UI", 10), justify="left", wraplength=460).pack(anchor="w", pady=(8, 16))
        local_var = tk.BooleanVar(value=True)
        pkg_var = tk.BooleanVar(value=False)
        cache_var = tk.BooleanVar(value=False)
        self._check(card, local_var, self.t("local_title"), self.t("local_sub"))
        self._check(card, pkg_var, self.t("pkg_title"), self.t("pkg_sub"))
        self._check(card, cache_var, self.t("cache_title"), self.t("cache_sub", path=MODEL_CACHE_DIR))
        tk.Label(card, text=self.t("dlg_note"), bg=CARD, fg=MUTED, font=("Segoe UI", 9), justify="left", wraplength=460).pack(anchor="w", pady=(14, 0))
        footer = tk.Frame(card, bg=CARD)
        footer.pack(fill="x", pady=(16, 0))
        tk.Button(footer, text=self.t("cancel"), command=dialog.destroy, bg=CARD_ALT, fg=TEXT, activebackground="#202938", activeforeground=TEXT,
                  highlightthickness=1, highlightbackground=BORDER, relief="flat", bd=0, font=("Segoe UI", 10, "bold"), padx=14, pady=9, cursor="hand2").pack(side="right")
        tk.Button(footer, text=self.t("continue"), command=lambda: self._confirm_uninstall(dialog, local_var.get(), pkg_var.get(), cache_var.get()),
                  bg=ACCENT, fg="#08131F", activebackground=ACCENT_HOVER, activeforeground="#08131F",
                  highlightthickness=1, highlightbackground=BORDER, relief="flat", bd=0, font=("Segoe UI", 10, "bold"), padx=16, pady=9, cursor="hand2").pack(side="right", padx=(0, 10))
        self._center_window(dialog)

    def _check(self, parent, variable, title, sub):
        wrap = tk.Frame(parent, bg=CARD_ALT, padx=14, pady=12, highlightthickness=1, highlightbackground=BORDER)
        wrap.pack(fill="x", pady=(0, 10))
        tk.Checkbutton(wrap, text=title, variable=variable, bg=CARD_ALT, fg=TEXT, selectcolor=CARD_ALT, activebackground=CARD_ALT,
                       activeforeground=TEXT, highlightthickness=0, bd=0, font=("Segoe UI", 10, "bold"), anchor="w").pack(anchor="w")
        tk.Label(wrap, text=sub, bg=CARD_ALT, fg=DIM, font=("Segoe UI", 9), justify="left", wraplength=420).pack(anchor="w", pady=(6, 0))

    def _confirm_uninstall(self, dialog, remove_local, remove_pkg, remove_cache):
        parts = []
        if remove_local:
            parts.append(f"- {self.t('summary_local')}")
        if remove_pkg:
            parts.append(f"- {self.t('summary_pkg')}")
        if remove_cache:
            parts.append(f"- {self.t('summary_cache')}")
        if not parts:
            messagebox.showinfo(self.t("nothing_title"), self.t("nothing_msg"), parent=dialog)
            return
        if not messagebox.askyesno(self.t("confirm_title"), self.t("confirm_msg", summary="\n".join(parts)), parent=dialog):
            return
        dialog.destroy()
        self.run_uninstall(remove_local, remove_pkg, remove_cache)

    def run_uninstall(self, remove_local, remove_pkg, remove_cache):
        if self._busy:
            return

        def worker():
            self.after(0, lambda: self._set_busy(True, "cleanup_busy"))
            if remove_local:
                for target in LOCAL_CLEAN_TARGETS:
                    try:
                        if target.is_dir():
                            shutil.rmtree(target, ignore_errors=False)
                        elif target.exists():
                            target.unlink()
                    except FileNotFoundError:
                        continue
                    except Exception as exc:
                        self.after(0, lambda t=target, e=exc: self._log(f"{t.name}: {e}"))
            if remove_cache:
                try:
                    if MODEL_CACHE_DIR.exists():
                        shutil.rmtree(MODEL_CACHE_DIR, ignore_errors=False)
                except Exception as exc:
                    self.after(0, lambda e=exc: self._log(str(e)))
            if remove_pkg:
                cmd = [python_cli_executable(), "-m", "pip", "uninstall", "-y", *UNINSTALL_PACKAGES]
                try:
                    proc = subprocess.Popen(cmd, cwd=str(APP_DIR), stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, creationflags=creation_flags())
                    assert proc.stdout is not None
                    for line in proc.stdout:
                        self.after(0, lambda text=line: self._log(text))
                    proc.wait()
                except Exception as exc:
                    self.after(0, lambda e=exc: self._log(str(e)))
            self.after(0, lambda: self._set_busy(False, "cleanup_done"))
            self.after(0, lambda: self.refresh_state(silent=True))
            self.after(0, lambda: messagebox.showinfo(self.t("cleanup_done_title"), self.t("cleanup_done_msg"), parent=self))

        threading.Thread(target=worker, daemon=True).start()


def main():
    app = Assistant(uninstall_only="--uninstall" in sys.argv[1:])
    app.mainloop()


if __name__ == "__main__":
    main()
