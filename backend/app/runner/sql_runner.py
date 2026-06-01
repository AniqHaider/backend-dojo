"""Runs a learner's SQL submission against a fresh, disposable Postgres schema.

For every run we create a uniquely-named schema, load the exercise's seed into it,
set search_path so the user's query sees the seed tables, run the query, compare the
result set to the expected rows, then DROP the schema. This keeps every attempt
isolated — a learner's DELETE/UPDATE can never affect another exercise.
"""
from __future__ import annotations

import datetime
import uuid
from decimal import Decimal

import psycopg

from ..config import PG_DSN, SEEDS_DIR


def _seed_statements(schema_key: str) -> list[str]:
    sql = (SEEDS_DIR / f"{schema_key}.sql").read_text()
    # strip comment lines, then split on ';'
    lines = [ln for ln in sql.splitlines() if not ln.strip().startswith("--")]
    body = "\n".join(lines)
    return [s.strip() for s in body.split(";") if s.strip()]


def _normalise(value):
    """Make DB values comparable to JSON-authored expected values."""
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime.datetime, datetime.date)):
        return value.isoformat()
    return value


def _rows_to_dicts(cur) -> list[dict]:
    cols = [d.name for d in cur.description]
    return [{c: _normalise(v) for c, v in zip(cols, row)} for row in cur.fetchall()]


def _row_key(row: dict) -> str:
    return repr(sorted(row.items(), key=lambda kv: kv[0]))


def _compare(got: list[dict], expected: list[dict], order_sensitive: bool) -> bool:
    if order_sensitive:
        return got == expected
    return sorted(got, key=_row_key) == sorted(expected, key=_row_key)


def run_sql_exercise(query: str, exercise: dict) -> dict:
    schema = "ex_" + uuid.uuid4().hex[:12]
    schema_key = exercise["schema_key"]
    expected = exercise.get("expected_query_result") or []
    order_sensitive = bool(exercise.get("order_sensitive", False))

    conn = psycopg.connect(PG_DSN, autocommit=True)
    try:
        with conn.cursor() as cur:
            cur.execute(f'CREATE SCHEMA "{schema}"')
            cur.execute(f'SET search_path TO "{schema}"')
            for stmt in _seed_statements(schema_key):
                cur.execute(stmt)
            # run the learner query in the same session/search_path
            try:
                cur.execute(query)
                rows = _rows_to_dicts(cur) if cur.description else []
            except psycopg.Error as e:
                return {"all_passed": False, "rows": [],
                        "error_category": "sql_error",
                        "detail": str(e).strip()}

        passed = _compare(rows, expected, order_sensitive)
        if passed:
            return {"all_passed": True, "rows": rows,
                    "error_category": None, "detail": None}
        return {"all_passed": False, "rows": rows,
                "error_category": "wrong_result",
                "detail": f"expected {expected}, got {rows}"}
    finally:
        try:
            with conn.cursor() as cur:
                cur.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
        finally:
            conn.close()
