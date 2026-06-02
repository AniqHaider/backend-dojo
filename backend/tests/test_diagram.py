from app.diagram import COMPONENTS, component_ids, components_to_unlock


def test_components_have_required_fields():
    for c in COMPONENTS:
        assert "id" in c and "label" in c and "chapter" in c and "group" in c


def test_client_always_present():
    assert "client" in component_ids()


def test_first_ch1_solve_unlocks_runtime():
    got = components_to_unlock(
        solved_ids={"ch1-ex01-greeting"},
        chapter_solved={1: False},
        chapter_totals={1: 13},
    )
    assert "py-runtime" in got


def test_chapter1_complete_unlocks_core():
    got = components_to_unlock(
        solved_ids={"ch1-ex01-greeting"},
        chapter_solved={1: True},
        chapter_totals={1: 13},
    )
    assert "ch1-complete-core" in got


def test_ch10_prefix_not_counted_as_ch1():
    # 'ch10-ex01' must NOT count toward chapter 1
    got = components_to_unlock(
        solved_ids={"ch10-ex01-retry"},
        chapter_solved={10: False},
        chapter_totals={1: 13, 10: 12},
    )
    assert "py-runtime" not in got
    assert "task-queue" in got  # ch10 'first'


def test_ch9_first_unlocks_cache():
    got = components_to_unlock(
        solved_ids={"ch9-ex01-ttl"},
        chapter_solved={9: False},
        chapter_totals={9: 12},
    )
    assert "redis-cache" in got


def test_nothing_unlocked_when_empty():
    got = components_to_unlock(solved_ids=set(), chapter_solved={}, chapter_totals={})
    assert got == set()
