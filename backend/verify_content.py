"""Dev script: run every exercise's reference_solution through the real runners and
report any that don't pass. Not part of the app; used to validate authored content.
"""
from app.content_loader import ContentLoader
from app.config import CONTENT_DIR
from app.grading import run_quiz_exercise
from app.runner.python_runner import run_python_exercise
from app.runner.sql_runner import run_sql_exercise

loader = ContentLoader(CONTENT_DIR)
failures = []
total = 0

for ch in loader.list_chapters():
    full = loader.get_chapter(ch["id"])  # public, no solutions
    for pub in full["exercises"]:
        total += 1
        ex = loader.get_exercise_full(pub["id"])
        ex_type = ex.get("type", "python")

        if ex_type == "quiz":
            ci = ex.get("correct_index")
            if ci is None:
                failures.append((ex["id"], "quiz missing correct_index"))
                continue
            if not ex.get("options") or not (0 <= ci < len(ex["options"])):
                failures.append((ex["id"], "quiz correct_index out of range"))
                continue
            r = run_quiz_exercise(str(ci), ex)
            status = "ok" if r["all_passed"] else "FAIL quiz answer mismatch"
            if not r["all_passed"]:
                failures.append((ex["id"], status))
            print(f"{'✓' if r['all_passed'] else '✗'} {ex['id']:30} {'' if r['all_passed'] else status}")
            continue

        ref = ex.get("reference_solution")
        if not ref:
            failures.append((ex["id"], "NO reference_solution"))
            continue
        if ex_type == "sql":
            r = run_sql_exercise(ref, ex)
        else:
            r = run_python_exercise(ref, ex)
        status = "ok" if r["all_passed"] else f"FAIL [{r['error_category']}] {r.get('detail')}"
        if not r["all_passed"]:
            failures.append((ex["id"], status))
        print(f"{'✓' if r['all_passed'] else '✗'} {ex['id']:28} {status if not r['all_passed'] else ''}")

print(f"\n{total - len(failures)}/{total} reference solutions pass.")
if failures:
    print("\nFAILURES:")
    for fid, msg in failures:
        print(f"  - {fid}: {msg}")
    raise SystemExit(1)
