"""Pure functions for XP→level conversion and daily streaks.

Kept free of I/O so they're trivially testable. The store and run endpoint call
into these.
"""
from __future__ import annotations

from datetime import date


def LEVEL_THRESHOLDS(level: int) -> int:
    """Cumulative XP required to *reach* a given level.

    Gentle quadratic curve: level 1 = 0, 2 = 100, 3 = 300, 4 = 600, 5 = 1000...
    Formula: 100 * n*(n-1)/2 where n = level-1 steps.
    """
    return 100 * (level - 1) * level // 2


def level_for_xp(xp: int) -> int:
    """Highest level whose threshold is <= xp."""
    level = 1
    while LEVEL_THRESHOLDS(level + 1) <= xp:
        level += 1
    return level


def next_streak(*, cur: int, last: str | None, today: str) -> int:
    """Compute the new streak given current streak, last active date, today.

    - No prior activity        -> 1
    - Same calendar day        -> unchanged
    - Exactly the next day     -> cur + 1
    - Any larger gap           -> 1 (reset)
    """
    if not last:
        return 1
    last_d = date.fromisoformat(last)
    today_d = date.fromisoformat(today)
    delta = (today_d - last_d).days
    if delta == 0:
        return cur
    if delta == 1:
        return cur + 1
    return 1
