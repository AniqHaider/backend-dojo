"""SQL runner tests. Require a local Postgres with the `backend_dojo` db.

If Postgres isn't reachable, these are skipped (so the rest of the suite still runs).
"""
import pytest

from app.runner.sql_runner import run_sql_exercise

try:
    import psycopg
    psycopg.connect("dbname=backend_dojo").close()
    PG_OK = True
except Exception:
    PG_OK = False

pytestmark = pytest.mark.skipif(not PG_OK, reason="Postgres backend_dojo not reachable")

BASE = {"schema_key": "ticketpay", "order_sensitive": False, "starter_code": ""}


def test_select_matches_expected():
    ex = {**BASE, "expected_query_result": [{"id": 1, "name": "Asha"}]}
    r = run_sql_exercise("SELECT id, name FROM users WHERE id = 1;", ex)
    assert r["all_passed"] is True
    assert r["error_category"] is None


def test_order_insensitive_match():
    ex = {**BASE, "expected_query_result": [{"name": "Ben"}, {"name": "Asha"}, {"name": "Chitra"}]}
    r = run_sql_exercise("SELECT name FROM users;", ex)
    assert r["all_passed"] is True


def test_wrong_result():
    ex = {**BASE, "expected_query_result": [{"id": 999}]}
    r = run_sql_exercise("SELECT id FROM users WHERE id = 1;", ex)
    assert r["all_passed"] is False
    assert r["error_category"] == "wrong_result"


def test_numeric_normalisation():
    ex = {**BASE, "expected_query_result": [{"title": "Dune", "rating": 8.5}]}
    r = run_sql_exercise("SELECT title, rating FROM movies WHERE id = 1;", ex)
    assert r["all_passed"] is True


def test_available_seats_capstone():
    ex = {**BASE, "expected_query_result": [{"label": "A3"}, {"label": "A4"}]}
    q = ("SELECT label FROM seats WHERE showtime_id = 1 "
         "AND id NOT IN (SELECT seat_id FROM bookings) ORDER BY label;")
    r = run_sql_exercise(q, ex)
    assert r["all_passed"] is True


def test_sql_error_category():
    ex = {**BASE, "expected_query_result": []}
    r = run_sql_exercise("SELEKT * FROM users;", ex)
    assert r["all_passed"] is False
    assert r["error_category"] == "sql_error"


def test_schema_is_dropped_after_run():
    # mutating the disposable schema must not leak into the next run
    ex = {**BASE, "expected_query_result": [{"count": 3}]}
    run_sql_exercise("DELETE FROM users;", {**BASE, "expected_query_result": []})
    r = run_sql_exercise("SELECT COUNT(*)::int AS count FROM users;", ex)
    assert r["all_passed"] is True  # still 3 -> previous DELETE was discarded
