#!/usr/bin/env bash
# Start Backend Dojo: Postgres (if needed), FastAPI backend (:4001), Svelte frontend (:4000).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

# Ensure Postgres is up (Homebrew service).
if ! pg_isready -q 2>/dev/null; then
  echo "Starting PostgreSQL…"
  brew services start postgresql@16 || true
  sleep 2
fi

cleanup() { echo; echo "Shutting down…"; kill 0; }
trap cleanup EXIT INT TERM

echo "Backend  → http://localhost:4001"
( cd "$ROOT/backend" && uv run uvicorn app.main:app --port 4001 --reload ) &

echo "Frontend → http://localhost:4000"
( cd "$ROOT/frontend" && npm run dev ) &

wait
