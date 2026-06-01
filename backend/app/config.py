from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BACKEND_DIR / "app" / "content"
SEEDS_DIR = BACKEND_DIR / "seeds"
PROGRESS_DB = BACKEND_DIR / "progress.db"

# Local Postgres created via `createdb backend_dojo`.
PG_DSN = "dbname=backend_dojo"

FRONTEND_ORIGIN = "http://localhost:4000"
PORT = 4001
