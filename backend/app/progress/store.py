"""SQLite-backed progress store.

This is the single source of truth for the learner's state: which exercises are
solved, how many attempts each took, a log of every mistake (used to personalise
the chat), global XP/level/streak stats, and which architecture-diagram components
have been unlocked.
"""
from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


class ProgressStore:
    def __init__(self, db_path: Path | str):
        self.db_path = str(db_path)

    def _conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_schema(self) -> None:
        with self._conn() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS exercise_progress (
                    exercise_id TEXT PRIMARY KEY,
                    status      TEXT NOT NULL DEFAULT 'unsolved',
                    attempts    INTEGER NOT NULL DEFAULT 0,
                    solved_at   TEXT,
                    best_code   TEXT
                );

                CREATE TABLE IF NOT EXISTS mistakes_log (
                    id             INTEGER PRIMARY KEY AUTOINCREMENT,
                    exercise_id    TEXT NOT NULL,
                    ts             TEXT NOT NULL,
                    error_category TEXT,
                    detail         TEXT
                );

                CREATE TABLE IF NOT EXISTS stats (
                    id              INTEGER PRIMARY KEY CHECK (id = 1),
                    xp              INTEGER NOT NULL DEFAULT 0,
                    level           INTEGER NOT NULL DEFAULT 1,
                    current_streak  INTEGER NOT NULL DEFAULT 0,
                    longest_streak  INTEGER NOT NULL DEFAULT 0,
                    last_active_date TEXT
                );

                CREATE TABLE IF NOT EXISTS diagram_state (
                    component_id TEXT PRIMARY KEY,
                    unlocked     INTEGER NOT NULL DEFAULT 0,
                    unlocked_at  TEXT
                );

                INSERT OR IGNORE INTO stats (id, xp, level, current_streak, longest_streak)
                VALUES (1, 0, 1, 0, 0);
                """
            )

    # ---- exercises -------------------------------------------------------
    def record_attempt(
        self,
        exercise_id: str,
        *,
        passed: bool,
        code: str,
        error_category: str | None = None,
        detail: str | None = None,
    ) -> None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT attempts, status FROM exercise_progress WHERE exercise_id = ?",
                (exercise_id,),
            ).fetchone()
            attempts = (row["attempts"] if row else 0) + 1
            already_solved = bool(row and row["status"] == "solved")

            if passed:
                status = "solved"
                solved_at = _now_iso() if not already_solved else None
                conn.execute(
                    """
                    INSERT INTO exercise_progress (exercise_id, status, attempts, solved_at, best_code)
                    VALUES (?, 'solved', ?, ?, ?)
                    ON CONFLICT(exercise_id) DO UPDATE SET
                        status='solved',
                        attempts=?,
                        best_code=excluded.best_code,
                        solved_at=COALESCE(exercise_progress.solved_at, excluded.solved_at)
                    """,
                    (exercise_id, attempts, solved_at or _now_iso(), code, attempts),
                )
            else:
                conn.execute(
                    """
                    INSERT INTO exercise_progress (exercise_id, status, attempts, best_code)
                    VALUES (?, 'unsolved', ?, ?)
                    ON CONFLICT(exercise_id) DO UPDATE SET
                        status=CASE WHEN exercise_progress.status='solved'
                                    THEN 'solved' ELSE 'unsolved' END,
                        attempts=?,
                        best_code=excluded.best_code
                    """,
                    (exercise_id, attempts, code, attempts),
                )
                conn.execute(
                    "INSERT INTO mistakes_log (exercise_id, ts, error_category, detail) "
                    "VALUES (?, ?, ?, ?)",
                    (exercise_id, _now_iso(), error_category, detail),
                )

    def get_exercise(self, exercise_id: str) -> dict:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM exercise_progress WHERE exercise_id = ?",
                (exercise_id,),
            ).fetchone()
        if not row:
            return {"exercise_id": exercise_id, "status": "unsolved",
                    "attempts": 0, "solved_at": None, "best_code": None}
        return dict(row)

    def all_progress(self) -> dict[str, dict]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM exercise_progress").fetchall()
        return {r["exercise_id"]: dict(r) for r in rows}

    def solved_ids(self) -> set[str]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT exercise_id FROM exercise_progress WHERE status='solved'"
            ).fetchall()
        return {r["exercise_id"] for r in rows}

    # ---- mistakes --------------------------------------------------------
    def log_mistake(self, exercise_id: str, error_category: str | None,
                    detail: str | None) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO mistakes_log (exercise_id, ts, error_category, detail) "
                "VALUES (?, ?, ?, ?)",
                (exercise_id, _now_iso(), error_category, detail),
            )

    def recent_mistakes(self, limit: int = 10) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT exercise_id, ts, error_category, detail FROM mistakes_log "
                "ORDER BY id DESC LIMIT ?",
                (limit,),
            ).fetchall()
        return [dict(r) for r in rows]

    # ---- stats -----------------------------------------------------------
    def get_stats(self) -> dict:
        with self._conn() as conn:
            row = conn.execute("SELECT * FROM stats WHERE id = 1").fetchone()
        return dict(row)

    def set_stats(self, *, xp: int, level: int, current_streak: int,
                  longest_streak: int, last_active_date: str | None) -> None:
        with self._conn() as conn:
            conn.execute(
                "UPDATE stats SET xp=?, level=?, current_streak=?, longest_streak=?, "
                "last_active_date=? WHERE id=1",
                (xp, level, current_streak, longest_streak, last_active_date),
            )

    # ---- diagram ---------------------------------------------------------
    def unlock_component(self, component_id: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT OR IGNORE INTO diagram_state (component_id, unlocked, unlocked_at) "
                "VALUES (?, 1, ?)",
                (component_id, _now_iso()),
            )

    def unlocked_components(self) -> list[str]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT component_id FROM diagram_state WHERE unlocked=1 "
                "ORDER BY unlocked_at"
            ).fetchall()
        return [r["component_id"] for r in rows]
