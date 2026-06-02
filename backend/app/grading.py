"""Ties a submission run to progress: execute -> record -> award XP/streak ->
unlock diagram components. Kept separate from the HTTP layer so it's unit-testable.
"""
from __future__ import annotations

from .content_loader import ContentLoader
from .diagram import components_to_unlock
from .progress.gamification import level_for_xp, next_streak
from .progress.store import ProgressStore
from .runner.python_runner import run_python_exercise
from .runner.sql_runner import run_sql_exercise


def _chapter_number(chapter_id: str) -> int | None:
    # 'ch1' -> 1, 'ch12' -> 12, 'ch99' -> 99
    digits = "".join(c for c in chapter_id if c.isdigit())
    return int(digits) if digits else None


def compute_chapter_solved(loader: ContentLoader, solved: set[str]) -> dict[int, bool]:
    out: dict[int, bool] = {}
    for ch in loader.list_chapters():
        n = _chapter_number(ch["id"])
        if n is None:
            continue
        ids = ch.get("exercise_ids", [])
        out[n] = bool(ids) and all(i in solved for i in ids)
    return out


def compute_chapter_totals(loader: ContentLoader) -> dict[int, int]:
    out: dict[int, int] = {}
    for ch in loader.list_chapters():
        n = _chapter_number(ch["id"])
        if n is None:
            continue
        out[n] = ch.get("exercise_count", len(ch.get("exercise_ids", [])))
    return out


def run_quiz_exercise(answer: str, exercise: dict) -> dict:
    """Grade a multiple-choice quiz. `answer` is the selected option index as a string."""
    try:
        choice = int(str(answer).strip())
    except (TypeError, ValueError):
        choice = -1
    correct = exercise.get("correct_index")
    passed = choice == correct
    return {
        "all_passed": passed,
        "selected": choice,
        "error_category": None if passed else "wrong_choice",
        "detail": None if passed else "That's not the best answer — read the explanation and try again.",
        "explanation": exercise.get("explanation_md", ""),
    }


def process_run(store: ProgressStore, loader: ContentLoader,
                exercise_id: str, code: str, today: str) -> dict:
    ex = loader.get_exercise_full(exercise_id)  # KeyError -> caller maps to 404
    ex_type = ex.get("type", "python")

    if ex_type == "sql":
        result = run_sql_exercise(code, ex)
        payload_key = "rows"
    elif ex_type == "quiz":
        result = run_quiz_exercise(code, ex)
        payload_key = "selected"
    else:
        result = run_python_exercise(code, ex)
        payload_key = "results"

    was_solved = store.get_exercise(exercise_id)["status"] == "solved"
    store.record_attempt(
        exercise_id,
        passed=result["all_passed"],
        code=code,
        error_category=result.get("error_category"),
        detail=result.get("detail"),
    )

    awarded_xp = 0
    new_components: list[str] = []

    if result["all_passed"] and not was_solved:
        xp = int(ex.get("xp", 10))
        stats = store.get_stats()
        new_xp = stats["xp"] + xp
        new_level = level_for_xp(new_xp)
        new_streak = next_streak(
            cur=stats["current_streak"],
            last=stats["last_active_date"],
            today=today,
        )
        new_longest = max(stats["longest_streak"], new_streak)
        store.set_stats(xp=new_xp, level=new_level, current_streak=new_streak,
                        longest_streak=new_longest, last_active_date=today)
        awarded_xp = xp

        solved = store.solved_ids()
        chapter_solved = compute_chapter_solved(loader, solved)
        chapter_totals = compute_chapter_totals(loader)
        to_unlock = components_to_unlock(solved_ids=solved,
                                         chapter_solved=chapter_solved,
                                         chapter_totals=chapter_totals)
        already = set(store.unlocked_components())
        for cid in to_unlock - already:
            store.unlock_component(cid)
            new_components.append(cid)

    return {
        "all_passed": result["all_passed"],
        payload_key: result.get(payload_key, []),
        "error_category": result.get("error_category"),
        "detail": result.get("detail"),
        "explanation": result.get("explanation"),
        "awarded_xp": awarded_xp,
        "new_components": new_components,
        "stats": store.get_stats(),
    }
