# Backend Dojo ⛩️

A playful, local dashboard for learning backend engineering by doing. Solve
in-browser exercises and watch your **TicketPay** architecture diagram grow from an
empty machine into a real `Client → FastAPI → PostgreSQL` backend. A built-in Claude
tutor knows your progress and your past mistakes.

- **Frontend:** Svelte 5 + Vite — http://localhost:4000
- **Backend:** FastAPI (Python 3.12 via uv) — http://localhost:4001
- **Database:** PostgreSQL (for the SQL chapter)
- **Tutor:** the local `claude` CLI, fed your progress + recent mistakes

## Chapters (first 3 of 12)
1. **Python Fundamentals** — 13 exercises
2. **Python Intermediate, Async & Tooling** — 13 exercises
3. **SQL Fundamentals (PostgreSQL)** — 13 exercises

Every exercise is graded by actually running your code (Python in a sandboxed
subprocess; SQL against a fresh, disposable Postgres schema).

## One-time setup
```bash
# 1. PostgreSQL (Homebrew)
brew install postgresql@16
brew services start postgresql@16
# put its CLI tools on PATH (Apple Silicon); add this line to ~/.zshrc to persist
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"
createdb backend_dojo

# 2. Backend deps (uv provisions Python 3.12)
cd backend && uv sync

# 3. Frontend deps
cd ../frontend && npm install
```
You also need the `claude` CLI installed and logged in for the chat panel.

## Run it
```bash
# from the project root
./scripts/dev.sh
```
Then open http://localhost:4000.

Or run the two processes manually:
```bash
# terminal 1
cd backend && uv run uvicorn app.main:app --port 4001 --reload
# terminal 2
cd frontend && npm run dev
```

## Cloning on another machine (with your data)
The repo carries the databases so a fresh clone has the practice data **and** your
saved progress:
- `db/ticketpay.sql` — the Postgres practice dataset (movies/showtimes/seats/bookings).
- `db/progress.sql` — a text dump of your sqlite progress (XP, solved exercises, streak,
  your code submissions). Auto-refreshed on every commit via a pre-commit hook.

After cloning and doing the one-time setup above, restore both with:
```bash
./scripts/db-restore.sh
```
This creates the Postgres `backend_dojo` database and rebuilds `backend/progress.db`
from `db/progress.sql`, so you continue exactly where you left off.

> Note: the binary `backend/progress.db` itself stays git-ignored; the diff-friendly
> `db/progress.sql` text dump is what's committed. To snapshot manually, run
> `./scripts/db-dump.sh`.

## Tests
```bash
cd backend && uv run pytest -q          # backend unit/integration tests
cd backend && uv run python verify_content.py   # every exercise's reference solution passes
```

## Adding more chapters later
Chapters are **data**, not code. Drop a new folder under
`backend/app/content/chapter-NN-name/` with `meta.json`, `theory.md`, and
`exercises/*.json` (ids starting `chN-ex...`). No code changes needed — the diagram
unlock rules in `app/diagram.py` already cover chapters 1–3; extend that list for 4+.

## Architecture
```
backend/app/
  content_loader.py   read chapter data, hide test/solution fields from the client
  diagram.py          canonical diagram components + unlock rules
  grading.py          run -> record -> award XP/streak -> unlock components
  runner/             python_runner.py (subprocess), sql_runner.py (disposable schema)
  progress/           store.py (sqlite), gamification.py (xp/level/streak)
  chat.py             build context + spawn `claude -p`
  main.py             FastAPI routes
frontend/src/
  lib/                api.js, stores.js
  components/         StatsBar, ArchitectureDiagram, ChapterList, LessonView,
                      ExerciseView, ResultsPanel, CodeEditor, ChatPanel
```
