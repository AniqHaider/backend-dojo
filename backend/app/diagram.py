"""Canonical architecture-diagram components and the rules that unlock them.

The diagram grows from an empty machine into a maturing backend as the learner
progresses through all 12 chapters: Client -> Application -> Data -> Infrastructure.

Each component declares:
  - group:   which visual zone it sits in (client/application/data/infrastructure)
  - chapter: which chapter unlocks it
  - unlock:  'first'    -> the learner has solved >=1 exercise in that chapter
             'mid'      -> solved >= half the chapter's exercises
             'complete' -> solved every exercise in the chapter

Rules are derived from per-chapter solve counts/totals, so authoring more exercises
never requires touching this file — only adding a new chapter's components does.
"""
from __future__ import annotations

import math

GROUPS = ["client", "application", "data", "infrastructure"]

COMPONENTS: list[dict] = [
    {"id": "client", "label": "Client (browser)", "group": "client", "chapter": 0, "always": True},

    # Application zone
    {"id": "py-runtime", "label": "Python runtime", "group": "application", "chapter": 1, "unlock": "first"},
    {"id": "functions", "label": "Functions", "group": "application", "chapter": 1, "unlock": "mid"},
    {"id": "data-structures", "label": "Data structures", "group": "application", "chapter": 1, "unlock": "mid"},
    {"id": "ch1-complete-core", "label": "App core", "group": "application", "chapter": 1, "unlock": "complete"},
    {"id": "type-system", "label": "Typed models", "group": "application", "chapter": 2, "unlock": "first"},
    {"id": "async-handler", "label": "Async handler", "group": "application", "chapter": 2, "unlock": "mid"},
    {"id": "request-router", "label": "Request router", "group": "application", "chapter": 2, "unlock": "complete"},
    {"id": "rest-api", "label": "REST API", "group": "application", "chapter": 5, "unlock": "first"},
    {"id": "endpoints", "label": "Endpoints", "group": "application", "chapter": 5, "unlock": "complete"},
    {"id": "validation", "label": "Validation", "group": "application", "chapter": 6, "unlock": "first"},
    {"id": "error-handling", "label": "Error handling", "group": "application", "chapter": 6, "unlock": "complete"},
    {"id": "auth-layer", "label": "Auth layer", "group": "application", "chapter": 7, "unlock": "first"},
    {"id": "rbac", "label": "Roles & access", "group": "application", "chapter": 7, "unlock": "complete"},
    {"id": "idempotency", "label": "Idempotency", "group": "application", "chapter": 8, "unlock": "complete"},

    # Data zone
    {"id": "postgres-db", "label": "PostgreSQL", "group": "data", "chapter": 3, "unlock": "first"},
    {"id": "tables", "label": "Tables", "group": "data", "chapter": 3, "unlock": "mid"},
    {"id": "joins-engine", "label": "Joins & queries", "group": "data", "chapter": 3, "unlock": "complete"},
    {"id": "indexes", "label": "Indexes", "group": "data", "chapter": 4, "unlock": "first"},
    {"id": "transactions", "label": "Transactions", "group": "data", "chapter": 4, "unlock": "complete"},
    {"id": "migrations", "label": "Migrations", "group": "data", "chapter": 6, "unlock": "mid"},
    {"id": "row-locks", "label": "Row locks", "group": "data", "chapter": 8, "unlock": "first"},

    # Infrastructure zone
    {"id": "redis-cache", "label": "Redis cache", "group": "infrastructure", "chapter": 9, "unlock": "first"},
    {"id": "rate-limiter", "label": "Rate limiter", "group": "infrastructure", "chapter": 9, "unlock": "complete"},
    {"id": "task-queue", "label": "Task queue", "group": "infrastructure", "chapter": 10, "unlock": "first"},
    {"id": "worker", "label": "Background worker", "group": "infrastructure", "chapter": 10, "unlock": "complete"},
    {"id": "test-suite", "label": "Test suite", "group": "infrastructure", "chapter": 11, "unlock": "first"},
    {"id": "docker", "label": "Docker", "group": "infrastructure", "chapter": 11, "unlock": "complete"},
    {"id": "load-balancer", "label": "Load balancer", "group": "infrastructure", "chapter": 12, "unlock": "first"},
    {"id": "read-replica", "label": "Read replica", "group": "infrastructure", "chapter": 12, "unlock": "complete"},
]


def component_ids() -> list[str]:
    return [c["id"] for c in COMPONENTS]


def _count_for_chapter(solved_ids: set[str], chapter: int) -> int:
    # Use the trailing dash so 'ch1-' never matches 'ch10-'/'ch12-'.
    prefix = f"ch{chapter}-"
    return sum(1 for sid in solved_ids if sid.startswith(prefix))


def components_to_unlock(*, solved_ids: set[str],
                         chapter_solved: dict[int, bool],
                         chapter_totals: dict[int, int] | None = None) -> set[str]:
    """Return the set of component ids that should be unlocked given progress."""
    chapter_totals = chapter_totals or {}
    counts = {}
    chapters = {c["chapter"] for c in COMPONENTS if c["chapter"] > 0}
    for ch in chapters:
        counts[ch] = _count_for_chapter(solved_ids, ch)

    unlocked: set[str] = set()
    for comp in COMPONENTS:
        if comp.get("always"):
            continue
        ch = comp["chapter"]
        rule = comp.get("unlock", "first")
        n = counts.get(ch, 0)
        total = chapter_totals.get(ch, 0)
        if rule == "first" and n >= 1:
            unlocked.add(comp["id"])
        elif rule == "mid" and total and n >= math.ceil(total / 2):
            unlocked.add(comp["id"])
        elif rule == "mid" and not total and n >= 1:
            # no totals available (e.g. unit test) — treat any progress as enough
            unlocked.add(comp["id"])
        elif rule == "complete" and chapter_solved.get(ch, False):
            unlocked.add(comp["id"])
    return unlocked
