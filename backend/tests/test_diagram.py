from app.diagram import COMPONENTS, component_ids, components_to_unlock


def test_components_have_required_fields():
    for c in COMPONENTS:
        assert "id" in c and "label" in c and "chapter" in c


def test_client_always_present():
    assert "client" in component_ids()


def test_first_ch1_solve_unlocks_runtime():
    got = components_to_unlock(
        solved_ids={"ch1-ex01-greeting"},
        chapter_solved={1: False, 2: False, 3: False},
    )
    assert "py-runtime" in got


def test_chapter1_complete_unlocks_core():
    got = components_to_unlock(
        solved_ids={"ch1-ex01-greeting"},
        chapter_solved={1: True, 2: False, 3: False},
    )
    assert "ch1-complete-core" in got


def test_first_ch3_solve_unlocks_postgres():
    got = components_to_unlock(
        solved_ids={"ch3-ex01-select"},
        chapter_solved={1: True, 2: True, 3: False},
    )
    assert "postgres-db" in got


def test_nothing_unlocked_when_empty():
    got = components_to_unlock(solved_ids=set(),
                               chapter_solved={1: False, 2: False, 3: False})
    # 'client' is always-on but not "unlocked" by progress
    assert "py-runtime" not in got
