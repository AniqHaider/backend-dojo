#!/usr/bin/env bash
# Snapshot the local databases into version-controllable files under db/.
# Run before committing so the repo always carries the latest DB state.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$ROOT/db"

# 1. Learner progress (sqlite) -> a text SQL dump (diff-friendly, unlike the binary .db).
if [ -f "$ROOT/backend/progress.db" ]; then
  sqlite3 "$ROOT/backend/progress.db" .dump > "$ROOT/db/progress.sql"
  echo "✓ db/progress.sql updated from backend/progress.db"
else
  echo "· no backend/progress.db yet — skipping progress dump"
fi

# 2. Postgres practice data is the static seed(s) under backend/seeds/, already in git.
#    Mirror the canonical seed into db/ so everything restorable lives in one place.
if [ -f "$ROOT/backend/seeds/ticketpay.sql" ]; then
  cp "$ROOT/backend/seeds/ticketpay.sql" "$ROOT/db/ticketpay.sql"
  echo "✓ db/ticketpay.sql synced from backend/seeds/ticketpay.sql"
fi
