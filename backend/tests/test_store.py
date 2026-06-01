from app.progress.store import ProgressStore


def make_store(tmp_path):
    s = ProgressStore(tmp_path / "p.db")
    s.init_schema()
    return s


def test_record_and_fetch_solve(tmp_path):
    s = make_store(tmp_path)
    s.record_attempt("ch1-ex01", passed=True, code="print(1)")
    p = s.get_exercise("ch1-ex01")
    assert p["status"] == "solved"
    assert p["attempts"] == 1
    assert p["best_code"] == "print(1)"
    assert p["solved_at"] is not None


def test_failed_attempt_logs_mistake_and_stays_unsolved(tmp_path):
    s = make_store(tmp_path)
    s.record_attempt(
        "ch1-ex02", passed=False, code="oops",
        error_category="wrong_output", detail="expected 5 got 0",
    )
    p = s.get_exercise("ch1-ex02")
    assert p["status"] == "unsolved"
    assert p["attempts"] == 1
    mistakes = s.recent_mistakes(limit=10)
    assert len(mistakes) == 1
    assert mistakes[0]["error_category"] == "wrong_output"
    assert mistakes[0]["exercise_id"] == "ch1-ex02"


def test_attempts_increment(tmp_path):
    s = make_store(tmp_path)
    s.record_attempt("ch1-ex03", passed=False, code="a", error_category="x")
    s.record_attempt("ch1-ex03", passed=True, code="b")
    p = s.get_exercise("ch1-ex03")
    assert p["attempts"] == 2
    assert p["status"] == "solved"


def test_unknown_exercise_returns_default(tmp_path):
    s = make_store(tmp_path)
    p = s.get_exercise("never-seen")
    assert p["status"] == "unsolved"
    assert p["attempts"] == 0


def test_stats_roundtrip(tmp_path):
    s = make_store(tmp_path)
    st = s.get_stats()
    assert st["xp"] == 0
    assert st["level"] == 1
    assert st["current_streak"] == 0
    s.set_stats(xp=120, level=2, current_streak=3, longest_streak=5,
                last_active_date="2026-06-01")
    st = s.get_stats()
    assert st["xp"] == 120
    assert st["level"] == 2
    assert st["longest_streak"] == 5
    assert st["last_active_date"] == "2026-06-01"


def test_diagram_unlock(tmp_path):
    s = make_store(tmp_path)
    assert s.unlocked_components() == []
    s.unlock_component("py-runtime")
    s.unlock_component("py-runtime")  # idempotent
    assert s.unlocked_components() == ["py-runtime"]


def test_solved_ids(tmp_path):
    s = make_store(tmp_path)
    s.record_attempt("a", passed=True, code="")
    s.record_attempt("b", passed=False, code="", error_category="x")
    assert s.solved_ids() == {"a"}
