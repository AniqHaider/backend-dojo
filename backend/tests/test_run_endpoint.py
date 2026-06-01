SOLUTION = "def add(a, b):\n    return a + b\n"
WRONG = "def add(a, b):\n    return 0\n"


def test_run_pass_awards_xp(client):
    r = client.post("/exercises/ch99-ex01-x/run", json={"code": SOLUTION})
    assert r.status_code == 200
    body = r.json()
    assert body["all_passed"] is True
    assert body["awarded_xp"] == 10
    assert body["stats"]["xp"] == 10


def test_run_xp_idempotent(client):
    client.post("/exercises/ch99-ex01-x/run", json={"code": SOLUTION})
    again = client.post("/exercises/ch99-ex01-x/run", json={"code": SOLUTION}).json()
    assert again["all_passed"] is True
    assert again["awarded_xp"] == 0          # no double XP
    assert again["stats"]["xp"] == 10


def test_run_fail_records_mistake(client):
    r = client.post("/exercises/ch99-ex01-x/run", json={"code": WRONG}).json()
    assert r["all_passed"] is False
    assert r["awarded_xp"] == 0
    assert r["error_category"] == "wrong_output"
    # mistake should now show in progress' chat-context surface
    prog = client.get("/progress").json()
    assert prog["xp"] == 0


def test_run_unknown_exercise_404(client):
    assert client.post("/exercises/nope/run", json={"code": "x"}).status_code == 404
