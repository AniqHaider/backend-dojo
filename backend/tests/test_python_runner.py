from app.runner.python_runner import run_python_exercise

EX = {"starter_code": "", "tests": [{"call": "total(2,3)", "expect": 5}]}


def test_pass():
    r = run_python_exercise("def total(a,b): return a+b", EX)
    assert r["all_passed"] is True
    assert r["results"][0]["passed"] is True
    assert r["error_category"] is None


def test_wrong_output():
    r = run_python_exercise("def total(a,b): return 0", EX)
    assert r["all_passed"] is False
    assert r["results"][0]["got"] == "0"
    assert r["error_category"] == "wrong_output"


def test_timeout():
    r = run_python_exercise("def total(a,b):\n while True: pass", EX)
    assert r["all_passed"] is False
    assert r["error_category"] == "timeout"


def test_syntax_error():
    r = run_python_exercise("def total(a,b) return a", EX)
    assert r["all_passed"] is False
    assert r["error_category"] == "syntax_error"


def test_runtime_error():
    r = run_python_exercise("def total(a,b): return a + missing", EX)
    assert r["all_passed"] is False
    assert r["error_category"] == "runtime_error"


def test_async_exercise():
    ex = {"tests": [{"call": "double(4)", "expect": 8}]}
    code = "import asyncio\nasync def double(n):\n    await asyncio.sleep(0)\n    return n*2\n"
    r = run_python_exercise(code, ex)
    assert r["all_passed"] is True


def test_multiple_tests_partial():
    ex = {"tests": [{"call": "f(1)", "expect": 1}, {"call": "f(2)", "expect": 99}]}
    r = run_python_exercise("def f(x): return x", ex)
    assert r["results"][0]["passed"] is True
    assert r["results"][1]["passed"] is False
    assert r["all_passed"] is False
