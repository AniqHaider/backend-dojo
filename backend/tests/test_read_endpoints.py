def test_health(client):
    assert client.get("/health").json() == {"ok": True}


def test_list_chapters(client):
    r = client.get("/chapters")
    assert r.status_code == 200
    data = r.json()
    assert data[0]["id"] == "ch99"
    assert data[0]["solved_count"] == 0


def test_get_chapter(client):
    r = client.get("/chapters/ch99")
    assert r.status_code == 200
    body = r.json()
    assert "fixture theory" in body["theory_md"]
    assert body["exercises"][0]["id"] == "ch99-ex01-x"
    assert "tests" not in body["exercises"][0]


def test_get_exercise_hides_tests(client):
    r = client.get("/exercises/ch99-ex01-x")
    assert r.status_code == 200
    assert "tests" not in r.json()


def test_get_unknown_exercise_404(client):
    assert client.get("/exercises/does-not-exist").status_code == 404


def test_progress_endpoint(client):
    r = client.get("/progress")
    assert r.status_code == 200
    body = r.json()
    assert body["xp"] == 0
    assert body["level"] == 1


def test_diagram_state_endpoint(client):
    r = client.get("/diagram-state")
    assert r.status_code == 200
    body = r.json()
    assert "components" in body
    assert body["unlocked"] == []
