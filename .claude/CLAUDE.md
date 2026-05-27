# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
# Install dependencies (first time or after pulling)
python -m pip install -r requirements.txt

# Run the app
python main.py

# Run the main screen directly (bypasses login/update check, useful during development)
python -m app.tela_principal   # opens with "Usuário Teste" — triggers admin features
```

There are no tests or linters configured in this project.

## Architecture

The app is a Windows desktop GUI built with **customtkinter** (tkinter wrapper). Entry point is `main.py`.

**Startup flow:**
1. `main.py` → `version_checker.check_for_updates()` — fetches `version.json` from GitHub; if outdated, shows `tela_update.TelaUpdate` and exits
2. → `tela_login.janela_login()` — shows the login window; validates credentials against SQLite via `bd.utils_bd.DatabaseManager`
3. On successful login → `tela_principal.janela(nome_usuario)` — creates `PDFMasterApp` and calls `mainloop()`

**Module responsibilities:**

| Module | Role |
|--------|------|
| `app/tela_principal.py` | Main window (`PDFMasterApp`). Three tabs: Imagem para PDF, Dividir PDF, Dividir PDF por Tamanho. Long operations run in `threading.Thread` to avoid blocking the UI. |
| `app/pdf_utils.py` | All PDF logic: `convert_to_pdf` (images→PDF via reportlab), `dividir_pdf_1` (page split via pypdf), `dividir_pdf_por_tamanho` (compress + split to ≤5 MB chunks). Uses `~/Documents/temp_folder` for intermediate files. |
| `app/tela_login.py` | Login and password-change windows (`LoginManager`). |
| `app/utils.py` | Shared UI helpers: `handle_error`, `IconManager`, `Tooltip`, `criar_pastas`, `exportar_log_tempo`, theme toggle. |
| `app/mensagens.py` | Context-aware greeting messages with day/holiday-based colour coding. |
| `app/componentes.py` | `CustomEntry` and `CustomComboBox` — pre-styled CTk widgets used across all screens. |
| `app/version_checker.py` | Reads local `version.json`; checks `raw.githubusercontent.com` for updates. |
| `app/tela_update.py` | Mandatory-update dialog shown when the remote version is newer. |
| `bd/utils_bd.py` | `DatabaseManager` — wraps an SQLite `dados_login` table with columns `nome_usuario`, `senha`, `nome_completo`, `abas`. |

## Key design patterns

**Dual-path imports** — every `app/` module uses a `try/except ImportError` pattern to support both package imports (`from .utils import …`) and direct execution (`from utils import …`). Don't break this symmetry.

**Hardcoded Google Drive paths** — several paths point to `G:\Meu Drive\…` (the primary database, icon, and log destination). Local fallbacks exist for each:
- Database: `app\bd\login.db` (relative)
- Icon: `app\assets\PDFMaster_icon.ico` (relative)
- Logs: `logs\` (relative)

**Admin detection** — `PDFMasterApp.admin_users = ["Usuário Teste", "Admin"]`. Users in this list get extra buttons (Nova Mensagem, Ver Paleta de Cores) and a taller window (`600x500` vs `600x450`).

**Thread safety** — `self.thread_rodando` flag prevents concurrent PDF operations. Button state changes back to the main thread via `widget.after(0, callback)`.

**Version management** — bump `version.json` at the repo root to trigger the mandatory-update prompt for existing users.

**Output file naming conventions:**
- Split pages: `{original_name}_{page_number}.pdf`
- Split by size: `PT{nn} {original_name}.pdf` (e.g. `PT01 relatorio.pdf`)
