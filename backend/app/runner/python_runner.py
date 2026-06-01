"""Runs a learner's Python submission against an exercise's hidden tests.

Strategy: write the user's code plus a small generated harness into a temp file,
execute it as a SEPARATE subprocess (so an infinite loop can be killed and a crash
can't take down the server), parse a JSON results marker from stdout, and classify
any failure.

Security: this executes arbitrary Python locally. Acceptable for a single-user,
localhost-only tool. Mitigations: separate subprocess, 5s timeout, isolated temp
dir, captured+capped output, no arguments/network passed in.
"""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

TIMEOUT_SECONDS = 5
MAX_OUTPUT = 20_000
RESULTS_MARKER = "__DOJO_RESULTS__"

_HARNESS = '''

# ---- dojo test harness (auto-generated) ----
import json as _dojo_json
import inspect as _dojo_inspect
import asyncio as _dojo_asyncio

_DOJO_TESTS = {tests!r}
_dojo_results = []
for _t in _DOJO_TESTS:
    try:
        _got = eval(_t["call"])
        if _dojo_inspect.iscoroutine(_got):
            _got = _dojo_asyncio.run(_got)
        _dojo_results.append({{
            "call": _t["call"],
            "passed": _got == _t["expect"],
            "expected": repr(_t["expect"]),
            "got": repr(_got),
        }})
    except Exception as _e:
        _dojo_results.append({{
            "call": _t["call"],
            "passed": False,
            "expected": repr(_t["expect"]),
            "got": None,
            "error": "{{}}: {{}}".format(type(_e).__name__, _e),
        }})
print("{marker}" + _dojo_json.dumps(_dojo_results))
'''


def _build_script(user_code: str, tests: list[dict]) -> str:
    return user_code + _HARNESS.format(tests=tests, marker=RESULTS_MARKER)


def _parse_results(stdout: str) -> list[dict] | None:
    for line in stdout.splitlines():
        if line.startswith(RESULTS_MARKER):
            return json.loads(line[len(RESULTS_MARKER):])
    return None


def run_python_exercise(code: str, exercise: dict) -> dict:
    tests = exercise.get("tests", [])
    script = _build_script(code, tests)

    with tempfile.TemporaryDirectory() as tmp:
        script_path = Path(tmp) / "submission.py"
        script_path.write_text(script)
        try:
            proc = subprocess.run(
                [sys.executable, str(script_path)],
                capture_output=True, text=True,
                timeout=TIMEOUT_SECONDS, cwd=tmp,
            )
        except subprocess.TimeoutExpired:
            return {
                "all_passed": False, "results": [],
                "error_category": "timeout",
                "detail": f"Execution exceeded {TIMEOUT_SECONDS}s (possible infinite loop).",
            }

    stdout = proc.stdout[:MAX_OUTPUT]
    stderr = proc.stderr[:MAX_OUTPUT]
    results = _parse_results(stdout)

    if results is None:
        # script crashed before printing results
        category = "syntax_error" if "SyntaxError" in stderr else "runtime_error"
        return {"all_passed": False, "results": [],
                "error_category": category, "detail": stderr.strip()[-1000:]}

    all_passed = all(r["passed"] for r in results)
    if all_passed:
        category = None
        detail = None
    elif any("error" in r for r in results):
        category = "runtime_error"
        detail = next(r["error"] for r in results if "error" in r)
    else:
        category = "wrong_output"
        first = next(r for r in results if not r["passed"])
        detail = f"{first['call']} -> expected {first['expected']}, got {first['got']}"

    return {"all_passed": all_passed, "results": results,
            "error_category": category, "detail": detail}
