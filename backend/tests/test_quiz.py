from app.grading import run_quiz_exercise

EX = {
    "type": "quiz",
    "options": ["A", "B", "C"],
    "correct_index": 1,
    "explanation_md": "B is correct because ...",
}


def test_correct_choice_passes():
    r = run_quiz_exercise("1", EX)
    assert r["all_passed"] is True
    assert r["explanation"].startswith("B is correct")


def test_wrong_choice_fails_with_explanation():
    r = run_quiz_exercise("0", EX)
    assert r["all_passed"] is False
    assert r["error_category"] == "wrong_choice"
    assert r["explanation"]  # still shown so the learner learns


def test_garbage_answer_fails():
    r = run_quiz_exercise("not-a-number", EX)
    assert r["all_passed"] is False
