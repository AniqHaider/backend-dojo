"""Canonical architecture-diagram components and the rules that unlock them.

The diagram grows from an empty machine into Client -> FastAPI handler -> Postgres
as the learner progresses. Unlock rules are based on how many exercises of each
chapter are solved (ids are expected to start with 'ch1'/'ch2'/'ch3') plus
chapter-complete flags. This keeps the rules independent of the exact exercise ids,
so authoring content later doesn't require touching this file.
"""
from __future__ import annotations

# Ordered left -> right; `edge` components are connections drawn between nodes.
COMPONENTS: list[dict] = [
    {"id": "client", "label": "Client (browser)", "chapter": 0, "kind": "node", "always": True},
    {"id": "py-runtime", "label": "Python runtime", "chapter": 1, "kind": "node"},
    {"id": "functions", "label": "Functions", "chapter": 1, "kind": "node"},
    {"id": "data-structures", "label": "Data structures", "chapter": 1, "kind": "node"},
    {"id": "ch1-complete-core", "label": "App core", "chapter": 1, "kind": "node"},
    {"id": "type-system", "label": "Typed models", "chapter": 2, "kind": "node"},
    {"id": "async-handler", "label": "Async handler", "chapter": 2, "kind": "node"},
    {"id": "request-router", "label": "Request router", "chapter": 2, "kind": "node"},
    {"id": "postgres-db", "label": "PostgreSQL", "chapter": 3, "kind": "node"},
    {"id": "tables", "label": "Tables", "chapter": 3, "kind": "node"},
    {"id": "joins-engine", "label": "Joins & queries", "chapter": 3, "kind": "node"},
    {"id": "db-connection", "label": "DB connection", "chapter": 3, "kind": "edge"},
]


def component_ids() -> list[str]:
    return [c["id"] for c in COMPONENTS]


def _count_for_chapter(solved_ids: set[str], chapter: int) -> int:
    prefix = f"ch{chapter}"
    return sum(1 for sid in solved_ids if sid.startswith(prefix))


# (component_id, predicate) — predicate(counts, chapter_solved) -> bool
def _rules():
    return [
        ("py-runtime", lambda c, done: c[1] >= 1),
        ("functions", lambda c, done: c[1] >= 4),
        ("data-structures", lambda c, done: c[1] >= 8),
        ("ch1-complete-core", lambda c, done: done.get(1, False)),
        ("type-system", lambda c, done: c[2] >= 1),
        ("async-handler", lambda c, done: c[2] >= 6),
        ("request-router", lambda c, done: done.get(2, False)),
        ("postgres-db", lambda c, done: c[3] >= 1),
        ("tables", lambda c, done: c[3] >= 4),
        ("joins-engine", lambda c, done: c[3] >= 8),
        ("db-connection", lambda c, done: done.get(3, False)),
    ]


def components_to_unlock(*, solved_ids: set[str],
                         chapter_solved: dict[int, bool]) -> set[str]:
    """Return the set of component ids that should be unlocked given progress."""
    counts = {ch: _count_for_chapter(solved_ids, ch) for ch in (1, 2, 3)}
    unlocked = set()
    for comp_id, pred in _rules():
        if pred(counts, chapter_solved):
            unlocked.add(comp_id)
    return unlocked
