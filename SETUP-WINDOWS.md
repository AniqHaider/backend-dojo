# Backend Dojo — Windows setup

A local learning app for backend engineering: **12 chapters, 76 Python + 24 SQL exercises, 47 quizzes**, XP/streaks, a
growing architecture diagram and an optional AI tutor.

| Part | Stack | Port |
|---|---|---|
| Frontend | Svelte 5 + Vite (CodeMirror editor) | **4000** |
| Backend | FastAPI (Python 3.12 via **uv**), SQLite for your progress | **4001** |
| SQL exercises | A real **PostgreSQL 16** database (each run uses a disposable schema) | 5432 |
| Tutor chat (optional) | the local `claude` CLI | — |

> **Easiest alternative:** the **Kata** app (`prep-pocket` repo) contains this whole Dojo running entirely in the browser /
> on your phone (Python via Pyodide, SQL via Postgres-in-WASM) — **no Python, no Postgres, no backend needed**. Use this
> guide only if you want the original FastAPI + Postgres version.

> **Status.** On macOS I verified from a **fresh clone**: `uv sync`, `uv run pytest -q` (**59 passed**),
> `uv run python verify_content.py` (**147/147 reference solutions pass**), the Python-based progress restore below, and
> the frontend `npm install` + `npm run build`. The Windows-specific steps (winget installs, PostgreSQL login settings,
> PowerShell commands) follow official docs but have **not been run on a real Windows PC yet**.
>
> The repo's helper scripts (`scripts\dev.sh`, `db-dump.sh`, `db-restore.sh`) are **Bash + Homebrew** specific — don't run
> them in PowerShell. This guide replaces them with plain commands.

---

## 1. Install the tools (PowerShell)

```powershell
winget install --id Git.Git -e
winget install --id astral-sh.uv -e                 # Python package/version manager (provisions Python 3.12 for you)
winget install --id OpenJS.NodeJS.LTS -e            # Node 22 LTS + npm for the frontend
winget install --id PostgreSQL.PostgreSQL.16 -e     # PostgreSQL 16 (interactive installer)
```

**PostgreSQL installer:** keep the default port **5432**, and **set a password** for the `postgres` superuser when asked
— remember it. You can untick *Stack Builder* at the end.

Close and reopen PowerShell, then check:

```powershell
git --version ; uv --version ; node --version ; npm --version
& "C:\Program Files\PostgreSQL\16\bin\psql.exe" --version
```

Add PostgreSQL's tools to PATH for your user (so `createdb`/`psql` work), then **open a new PowerShell**:

```powershell
$p = [Environment]::GetEnvironmentVariable("Path", "User")
[Environment]::SetEnvironmentVariable("Path", "$p;C:\Program Files\PostgreSQL\16\bin", "User")
```

## 2. Tell the backend how to log in to PostgreSQL

The backend connects with just `dbname=backend_dojo` (see `backend\app\config.py`), so it relies on libpq's standard
environment variables for the rest. Set them **persistently** (use the password you chose in step 1):

```powershell
[Environment]::SetEnvironmentVariable("PGHOST", "localhost", "User")
[Environment]::SetEnvironmentVariable("PGUSER", "postgres", "User")
[Environment]::SetEnvironmentVariable("PGPASSWORD", "YOUR_POSTGRES_PASSWORD", "User")
```

Open a **new** PowerShell, then create the practice database (one time):

```powershell
createdb backend_dojo
```

(`createdb: error: database "backend_dojo" already exists` is fine.) The SQL runner loads `backend\seeds\ticketpay.sql`
into a throw-away schema for every run, so there's nothing else to import.

> Using a different Postgres user/port? Set `PGUSER`, `PGPORT` etc. accordingly — or edit `PG_DSN` in
> `backend\app\config.py`.

## 3. Clone and install

```powershell
mkdir C:\dev ; cd C:\dev
git clone https://github.com/AniqHaider/backend-dojo.git
cd backend-dojo

# backend (uv downloads Python 3.12 automatically)
cd backend
uv sync

# frontend
cd ..\frontend
npm install
cd ..
```

## 4. (Optional) Restore your saved progress

The repo carries a text dump of the author's progress (`db\progress.sql`: XP, solved exercises, streak, code
submissions). To start **with** that progress instead of a blank slate — run from `backend\`:

```powershell
cd C:\dev\backend-dojo\backend
uv run python -c "import sqlite3, pathlib; p = pathlib.Path('progress.db'); p.unlink(missing_ok=True); c = sqlite3.connect(p); c.executescript(pathlib.Path('../db/progress.sql').read_text(encoding='utf-8')); c.commit(); print('restored')"
```

(This replaces `scripts\db-restore.sh`; no `sqlite3` CLI is required.) Skip this step to start fresh — the backend creates
`progress.db` automatically.

## 5. Run it (two PowerShell windows)

**Window 1 — backend:**

```powershell
cd C:\dev\backend-dojo\backend
uv run uvicorn app.main:app --port 4001 --reload
```

**Window 2 — frontend:**

```powershell
cd C:\dev\backend-dojo\frontend
npm run dev
```

Open **http://localhost:4000**. The frontend needs the backend on `http://localhost:4001` (CORS is configured for
`http://localhost:4000` — keep those ports; the frontend uses `strictPort`).

Allow the Windows Firewall prompt for Python/Node if it appears (only needed for access from other devices).

## 6. Tests and content check

```powershell
cd C:\dev\backend-dojo\backend
uv run pytest -q                    # expect: 59 passed
uv run python verify_content.py     # expect: 147/147 reference solutions pass
```

`pytest` and `verify_content.py` need PostgreSQL running with the `backend_dojo` database (steps 1–2) for the SQL
exercises.

## 7. The AI tutor (optional)

The chat panel shells out to the **`claude` CLI** (`claude -p …`). Without it everything else works; the tutor replies
"(Tutor unavailable: …)". To enable it, install Claude Code for Windows and log in once (`claude`), making sure
`claude` runs from the same terminal that starts the backend.

No Claude on the new PC? Use the **Kata** app instead — its tutor can run an open model on your phone, or call Gemini /
Claude / an Ollama server.

## 8. Adding chapters

Chapters are data: add `backend\app\content\chapter-NN-name\` with `meta.json`, `theory.md` and `exercises\*.json`
(ids starting `chN-ex…`). No code change is needed; the diagram-unlock rules live in `backend\app\diagram.py`.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `uv` / `node` / `createdb` "not recognized" | Close and reopen PowerShell; re-check the PATH step in section 1. |
| `psycopg.OperationalError … password authentication failed` / `role "<your-windows-name>" does not exist` | `PGUSER` / `PGPASSWORD` not set (section 2) — set them and open a **new** terminal. |
| `connection refused` on 5432 | PostgreSQL service not running: Start menu → *Services* → `postgresql-x64-16` → Start. |
| SQL exercises fail with `database "backend_dojo" does not exist` | Run `createdb backend_dojo` (section 2). |
| Frontend shows "Can't reach the backend" | Backend window must be running on port **4001**; check for errors there. |
| `Port 4000 is already in use` | Close the other process (`netstat -ano | findstr :4000`, then `taskkill /PID <pid> /F`); the app requires port 4000. |
| `Python 3.12 not found` | `uv python install 3.12`, then `uv sync` again. |
| Script/`.sh` errors | Don't use the `.sh` scripts on Windows; use the commands in this guide. |
| Git hook noise on commit | The author's local pre-commit hook (a `.git\hooks` file, not part of a clone) refreshes `db\progress.sql`; a fresh clone has no hook. |
