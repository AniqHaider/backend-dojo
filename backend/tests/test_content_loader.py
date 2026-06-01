from pathlib import Path

from app.content_loader import ContentLoader

FIXTURE = Path(__file__).parent / "fixtures" / "content"


def test_lists_chapters():
    loader = ContentLoader(FIXTURE)
    chapters = loader.list_chapters()
    assert len(chapters) == 1
    assert chapters[0]["id"] == "ch99"
    assert chapters[0]["title"] == "Test Chapter"
    assert chapters[0]["exercise_count"] == 1


def test_get_chapter_includes_theory_and_public_exercises():
    loader = ContentLoader(FIXTURE)
    ch = loader.get_chapter("ch99")
    assert "fixture theory" in ch["theory_md"]
    assert ch["exercises"][0]["id"] == "ch99-ex01-x"
    # public listing must not leak tests
    assert "tests" not in ch["exercises"][0]


def test_public_exercise_hides_tests():
    loader = ContentLoader(FIXTURE)
    ex = loader.get_exercise_public("ch99-ex01-x")
    assert ex["title"] == "Add two numbers"
    assert "tests" not in ex
    assert "starter_code" in ex
    assert "hints" in ex


def test_full_exercise_keeps_tests():
    loader = ContentLoader(FIXTURE)
    full = loader.get_exercise_full("ch99-ex01-x")
    assert "tests" in full
    assert full["tests"][0]["expect"] == 5


def test_unknown_exercise_raises():
    loader = ContentLoader(FIXTURE)
    try:
        loader.get_exercise_full("nope")
        assert False, "should raise"
    except KeyError:
        pass
