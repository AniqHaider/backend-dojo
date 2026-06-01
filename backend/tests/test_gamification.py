from app.progress.gamification import level_for_xp, next_streak, LEVEL_THRESHOLDS


def test_level_curve():
    assert level_for_xp(0) == 1
    assert level_for_xp(99) == 1
    assert level_for_xp(100) == 2
    assert level_for_xp(299) == 2
    assert level_for_xp(300) == 3
    assert level_for_xp(600) == 4


def test_thresholds_monotonic():
    vals = [LEVEL_THRESHOLDS(n) for n in range(1, 8)]
    assert vals == sorted(vals)
    assert vals[0] == 0


def test_streak_same_day_no_double():
    assert next_streak(cur=3, last="2026-06-01", today="2026-06-01") == 3


def test_streak_next_day_increments():
    assert next_streak(cur=3, last="2026-06-01", today="2026-06-02") == 4


def test_streak_gap_resets():
    assert next_streak(cur=3, last="2026-06-01", today="2026-06-04") == 1


def test_streak_first_ever():
    assert next_streak(cur=0, last=None, today="2026-06-01") == 1


def test_streak_month_boundary():
    assert next_streak(cur=2, last="2026-05-31", today="2026-06-01") == 3
