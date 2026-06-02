#!/usr/bin/env bash
# Restore the databases on a freshly cloned machine.
#   - creates the Postgres practice DB (SQL exercises seed themselves per-run)
#   - rebuilds the sqlite progress DB from the committed text dump
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PATH="/opt/homebrew/opt/postgresql@16/bin:$PATH"

echo "== Postgres =="
if command -v createdb >/dev/null 2>&1; then
  if createdb backend_dojo 2>/dev/null; then
    echo "✓ created Postgres database 'backend_dojo'"
  else
    echo "· Postgres database 'backend_dojo' already exists (ok)"
  fi
  echo "  (SQL exercises load db/ticketpay.sql into a disposable schema automatically)"
else
  echo "! createdb not found — install postgresql@16 and put its bin on PATH"
fi

echo "== Learner progress =="
if [ -f "$ROOT/db/progress.sql" ]; then
  rm -f "$ROOT/backend/progress.db"
  sqlite3 "$ROOT/backend/progress.db" < "$ROOT/db/progress.sql"
  echo "✓ restored backend/progress.db from db/progress.sql"
else
  echo "· no db/progress.sql in repo — you'll start with fresh progress"
fi
