# Background Remover Studio

> **[English](#english) | [Português BR](#português-br)**

---

## English

### How to use

1. Download this folder
2. Double-click **`start.exe`**
3. Click **Install** on first run, then **Open App**

That's it. No technical knowledge needed.

> **First run:** The app will download the AI model (~170 MB) automatically. After that it works fully offline.

---

### For developers

A free, local, and privacy-first background remover. Everything runs on your machine — no internet required after the first model download, no account, no upload limits.

#### Features

- Modern dark desktop UI with English / Portuguese toggle
- Batch background removal (process multiple images at once)
- Drag and drop image import
- Adaptive processing — different logic for photos vs. artwork/logos
- Edge refinement tools (smoothing, erosion, hair protection)
- Export to PNG, WebP, TIFF, JPG, and BMP
- Copy processed output directly to the clipboard
- Guided setup assistant (install, repair, and cleanup — all in a GUI)
- REST API for integrations (ChatGPT Custom Actions, scripts — see `tools/`)
- Web UI coming soon

#### Requirements

- Windows 10 or 11
- Python 3.10 or higher — [python.org](https://www.python.org/downloads/)

#### Run from source

```bash
pip install -r requirements.txt
python src/main.py
```

#### Build the installer

```bat
build.bat
```

Requires [Inno Setup 6](https://jrsoftware.org/isdl.php) installed. The script compiles everything and produces `BackgroundRemoverStudio_Setup.exe` in the project root.

#### Project structure

```
background-remover-studio/
├── BackgroundRemoverStudio_Setup.exe  # Installer — end users start here
├── build.bat                          # Build script
├── main.spec                          # PyInstaller config (main app)
├── launcher.spec                      # PyInstaller config (start.exe)
├── requirements.txt                   # Python dependencies
├── LICENSE
├── README.md
├── src/
│   ├── main.py                        # Desktop app entry point
│   ├── background_remover.py          # UI + AI pipeline
│   ├── api_server.py                  # FastAPI server (API product)
│   ├── setup_assistant.pyw            # Setup / repair / cleanup GUI
│   ├── launcher.py                    # start.exe source
│   ├── _paths.py                      # Path resolution for frozen builds
│   └── icon.ico
├── installer/
│   └── setup.iss                      # Inno Setup script
├── tools/
│   ├── openapi_action.yaml            # ChatGPT Custom Action schema
│   ├── claude_tool.json               # Claude tool definition
│   └── chatgpt_action.json            # GPT setup instructions
└── scripts/
    └── dev-run.bat                    # Dev launcher (no build needed)
```

#### Export formats

| Format | Transparency | Notes |
|---|---|---|
| PNG | ✅ | Lossless, recommended |
| WebP | ✅ | Smaller file size |
| TIFF | ✅ | Lossless, for print |
| JPG | ❌ | White background fill |
| BMP | ❌ | White background fill |

#### License

MIT — see [LICENSE](LICENSE)

#### Author

**Henrique Fernandes** — OportuniPT
henriquehsf@oportunipt.com
Instagram: [@oportunipt](https://instagram.com/oportunipt)

---

## Português BR

### Como usar

1. Baixe esta pasta
2. Dê dois cliques em **`BackgroundRemoverStudio_Setup.exe`**
3. Instale e use

Só isso. Não precisa saber nada de tecnologia.

> **Primeiro uso:** O app vai baixar o modelo de IA (~170 MB) automaticamente na primeira vez que você remover um fundo. Depois disso funciona completamente sem internet.

---

### Para desenvolvedores

Removedor de fundo gratuito, local e com privacidade total. Tudo roda na sua máquina — sem internet depois do primeiro download, sem conta, sem limite de uploads.

#### Funcionalidades

- Interface desktop dark moderna com botão English / Português
- Remoção em lote (várias imagens de uma vez)
- Importação por arrastar e soltar
- Processamento adaptativo — lógica diferente para fotos vs. arte/logos
- Ferramentas de refinamento de borda (suavização, erosão, proteção de cabelo)
- Exportação em PNG, WebP, TIFF, JPG e BMP
- Copiar resultado para a área de transferência
- Assistente de setup guiado (instalar, reparar, limpar — tudo em GUI)
- API REST para integrações (ChatGPT, scripts — veja `tools/`)
- Interface Web em breve

#### Requisitos

- Windows 10 ou 11
- Python 3.10 ou superior — [python.org](https://www.python.org/downloads/)

#### Rodar pelo código fonte

```bash
pip install -r requirements.txt
python src/main.py
```

#### Gerar o instalador

```bat
build.bat
```

Requer o [Inno Setup 6](https://jrsoftware.org/isdl.php) instalado. O script compila tudo e gera o `BackgroundRemoverStudio_Setup.exe` na raiz do projeto.

#### Licença

MIT — veja [LICENSE](LICENSE)

#### Autor

**Henrique Fernandes** — OportuniPT
henriquehsf@oportunipt.com
Instagram: [@oportunipt](https://instagram.com/oportunipt)
