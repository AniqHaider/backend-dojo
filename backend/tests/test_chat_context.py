from app.chat import build_context, system_prompt_for


def test_context_includes_mistakes_and_exercise():
    ctx = build_context(
        question="why does my code fail?",
        current_exercise={"id": "ch1-ex01", "title": "Add", "prompt_md": "do x",
                          "best_code": "def add(): pass"},
        recent_mistakes=[{"exercise_id": "ch1-ex01", "error_category": "wrong_output",
                          "detail": "expected 5 got 0"}],
        solved=["ch1-ex00"],
    )
    assert "wrong_output" in ctx
    assert "do x" in ctx
    assert "why does my code fail?" in ctx
    assert "ch1-ex00" in ctx


def test_context_handles_no_exercise():
    ctx = build_context(question="what is a list?", current_exercise=None,
                        recent_mistakes=[], solved=[])
    assert "what is a list?" in ctx


def test_tutor_prompt_is_socratic():
    p = system_prompt_for("tutor").lower()
    assert "hint" in p or "socratic" in p or "do not give" in p


def test_explain_prompt_is_direct():
    p = system_prompt_for("explain").lower()
    assert "explain" in p or "direct" in p


def test_unknown_mode_defaults_to_tutor():
    assert system_prompt_for("bogus") == system_prompt_for("tutor")
