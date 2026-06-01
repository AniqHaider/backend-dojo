# Backend Dojo — Design Spec

**Date:** 2026-06-01
**Author:** prepared with Aniq Haider
**Status:** Approved design, pre-implementation
**Project root:** `/Users/aniqhaider/projects/backend-dojo/`

---

## 1. Purpose

An interactive, playful learning dashboard that teaches Aniq backend engineering
**by doing** — starting from the first 3 chapters of his 12-week Python + PostgreSQL
plan. Aniq is a strong **frontend** engineer but **new to backend**, so theory must be
written from scratch with heavy "why," concrete analogies, and zero assumed backend
jargon.

The dashboard is itself a real FastAPI + Postgres backend, so the tool teaching backend
**is** an example of the thing being learned — Aniq can read its source as a reference.

**Success criteria:**
- Aniq can work through ~12 exercises per chapter for 3 chapters, in-browser.
- Solving an exercise visibly edits the dashboard (a component is added to a growing
  architecture diagram) and awards XP/level/streak.
- A built-in Claude chat answers his questions with the context of his progress and his
  past mistakes, in either a Socratic "Tutor" mode or a direct "Explain" mode.
- Adding chapters 4–12 later requires only adding content files, not code changes.

---

## 2. High-Level Architecture

```
/Users/aniqhaider/projects/backend-dojo/
├── backend/      FastAPI · Python 3.12 (managed by uv) · http://localhost:4001
├── frontend/     Svelte 5 + Vite (SPA, no SSR)          · http://localhost:4000
└── docs/specs/   this design doc
```

Two independent processes. Frontend is a static SPA that talks to the backend over
HTTP (CORS allows `http://localhost:4000`). The backend owns all state.

**Why this split:** clean separation of concerns, and it mirrors a real production setup
(SPA frontend + API backend) so Aniq learns the shape of real systems.

---

## 3. Backend (`backend/`, port 4001)

### 3.1 Stack
- **Python 3.12** provisioned via `uv` (isolated; system Python 3.9 is untouched).
- **FastAPI** + **uvicorn** (async web framework + server).
- **psycopg** (v3) for Postgres access in the SQL runner.
- **sqlite3** (Python stdlib) for the progress store.
- Standard lib `subprocess`, `tempfile`, `asyncio` for the code runner and chat proxy.

### 3.2 Content as data (not code)
Each chapter is **data**, so chapters 4–12 are added later with no code change:

```
backend/app/content/
├── chapter-01-python-fundamentals/
│   ├── meta.json            # title, summary, order, diagram milestone mapping
│   ├── theory.md            # long, beginner-friendly theory (rendered in FE)
│   └── exercises/
│       ├── 01-greeting.json
│       ├── 02-types.json
│       └── ...              # one JSON per exercise
├── chapter-02-python-intermediate-async/
└── chapter-03-sql-fundamentals/
```

**Exercise JSON shape (Python exercise):**
```json
{
  "id": "ch1-ex03-arithmetic",
  "title": "Arithmetic & operators",
  "type": "python",
  "prompt_md": "Write a function `total_price(qty, unit)` that returns qty * unit...",
  "starter_code": "def total_price(qty, unit):\n    # your code here\n    pass\n",
  "hints": ["Multiplication uses *", "Remember to return, not print"],
  "tests": [
    {"call": "total_price(3, 10)", "expect": 30},
    {"call": "total_price(0, 99)", "expect": 0}
  ],
  "xp": 10,
  "concept_tags": ["operators", "functions"]
}
```

**Exercise JSON shape (SQL exercise):**
```json
{
  "id": "ch3-ex09-inner-join",
  "title": "INNER JOIN bookings to users",
  "type": "sql",
  "prompt_md": "Return each booking's id alongside the user's name...",
  "schema_key": "ticketpay",          // which seed schema to load
  "starter_code": "SELECT ...;",
  "hints": ["JOIN ... ON ...", "Match bookings.user_id to users.id"],
  "expected_query_result": [ {"booking_id": 1, "name": "Asha"} ],
  "order_sensitive": false,
  "xp": 20,
  "concept_tags": ["join", "inner-join"]
}
```

### 3.3 Python exercise runner (`app/runner/python_runner.py`)
1. Write the user's submitted code to a temp file in a fresh temp dir.
2. Append a generated harness that imports it and runs each `tests[].call`, comparing to
   `expect`.
3. Execute with `uv run python` (Python 3.12) as a **subprocess** with:
   - **5-second timeout** (kills runaway/infinite loops),
   - **captured stdout/stderr** (output size capped),
   - no network needed, runs in the isolated temp dir.
4. Return per-test `{passed, expected, got, error}`.

**Security note:** this executes arbitrary local Python. Acceptable for a **single-user,
localhost-only** tool. Mitigations: subprocess isolation, timeout, temp dir, output cap.
Documented as an accepted risk; not exposed to any network.

### 3.4 SQL exercise runner (`app/runner/sql_runner.py`)
1. For the exercise's `schema_key`, create a **fresh, disposable schema** (or temp
   database) in Postgres and seed it with known data.
2. Run the user's query.
3. Compare the returned rows to `expected_query_result` (order-insensitive unless
   `order_sensitive`).
4. Drop the schema. Return rows + pass/fail + DB error message if any.

Seed domain = **TicketPay**: `users`, `movies`, `showtimes`, `seats`, `bookings`. This is
deliberately the capstone's domain so SQL practice maps to the project he'll build.

### 3.5 Progress store (`app/progress/`, sqlite `progress.db`)
Tables:
- `exercise_progress(exercise_id TEXT PK, status TEXT, attempts INT, solved_at TEXT, best_code TEXT)`
  — status ∈ {`locked`, `unsolved`, `solved`}.
- `mistakes_log(id INTEGER PK, exercise_id TEXT, ts TEXT, error_category TEXT, detail TEXT)`
  — every failed attempt, categorized (e.g. `syntax_error`, `wrong_output`,
  `timeout`, `sql_error`). **This feeds the chat's personalization.**
- `stats(id INTEGER PK CHECK(id=1), xp INT, level INT, current_streak INT, longest_streak INT, last_active_date TEXT)`
  — single-row global stats.
- `diagram_state(component_id TEXT PK, unlocked INT, unlocked_at TEXT)`.

### 3.6 Gamification rules
- **XP:** each exercise has an `xp` value (harder = more). Awarded once, on first solve.
- **Level:** thresholds (e.g. level n at `100 * n * (n-1) / 2` cumulative XP — gentle curve).
  Exact curve finalized in the plan.
- **Streak:** `current_streak` increments when the user solves ≥1 exercise on a calendar
  day after solving on the prior day; resets if a day is skipped. `longest_streak` tracks
  the max.
- **Diagram:** each chapter's `meta.json` maps exercises/milestones → diagram component
  ids. Solving the mapped exercise sets that component `unlocked=1`.

### 3.7 The architecture diagram (the creative payoff)
A canonical component list, revealed progressively. By end of Ch3 it forms
**Client → FastAPI handler → Postgres**:

| Component id | Unlocks when | Chapter |
|---|---|---|
| `client` | start (always visible, dim) | — |
| `py-runtime` | first Ch1 exercise solved | 1 |
| `functions` | Ch1 functions exercise solved | 1 |
| `data-structures` | Ch1 collections exercises solved | 1 |
| `ch1-complete-core` | all Ch1 solved | 1 |
| `type-system` | Ch2 typing/dataclass solved | 2 |
| `async-handler` | Ch2 async exercises solved | 2 |
| `request-router` | Ch2 complete | 2 |
| `postgres-db` | first Ch3 exercise solved | 3 |
| `tables` | Ch3 DDL/insert solved | 3 |
| `joins-engine` | Ch3 join exercises solved | 3 |
| `db-connection` (wires handler→db) | Ch3 complete | 3 |

Frontend renders this as an animated SVG; solving an exercise animates the relevant
component in.

### 3.8 Chat proxy (`app/chat.py`)
- Endpoint `POST /chat` receives `{question, mode, current_exercise_id}`.
- Builds a **context block** from the progress store:
  - current chapter/exercise + its prompt,
  - list of solved vs unsolved,
  - recent entries from `mistakes_log` (so it can say "you keep forgetting to `return`"),
  - the user's last submitted code for the current exercise (if any).
- Selects a **system prompt** by `mode`:
  - **Tutor** (default for exercises): Socratic — hints, leading questions, never hands a
    full exercise solution; references his specific past mistakes.
  - **Explain** (for theory questions): direct, clear explanations with examples.
- Spawns the **`claude` CLI headless**: `claude -p "<assembled prompt>" --append-system-prompt "<mode prompt>"`
  (exact flags verified during implementation), captures stdout, returns the text.
- Latency: a few seconds per call; uses Aniq's Claude quota. Documented.

### 3.9 API endpoints
| Method | Path | Purpose |
|---|---|---|
| GET | `/chapters` | list chapters + per-chapter progress summary |
| GET | `/chapters/{id}` | chapter theory (md) + ordered exercise list |
| GET | `/exercises/{id}` | one exercise (prompt, starter, hints — **not** hidden tests) |
| POST | `/exercises/{id}/run` | run submission → results; on pass, award XP + unlock diagram |
| GET | `/progress` | xp, level, streak, solved counts |
| GET | `/diagram-state` | unlocked components |
| POST | `/chat` | context-aware Claude chat (tutor/explain) |

---

## 4. Frontend (`frontend/`, port 4000)

### 4.1 Stack
- **Svelte 5** + **Vite** (SPA). No SSR — it's a local single-user app.
- **CodeMirror 6** — in-browser code/SQL editor with syntax highlighting.
- **marked** (+ sanitizer) — render theory markdown.
- Light state store (Svelte stores) for progress/diagram; no heavy framework.

### 4.2 Views / layout
- **Dashboard (home):** the living TicketPay architecture diagram (SVG, grows as you
  solve), XP bar, current level, streak flame, per-chapter completion rings, "continue"
  button.
- **Lesson view:** rendered theory.md (long, beginner-friendly) with inline concept
  checks; a sidebar lists the chapter's exercises with solved/unsolved markers.
- **Exercise view:** prompt (md) + CodeMirror editor (prefilled with starter_code) + Run
  button + results panel (per-test pass/fail with expected vs got). On all-green: success
  animation, XP pop, and the diagram component animates in.
- **Chat panel:** dockable side panel, **Tutor ⇄ Explain** toggle, message thread, knows
  the current exercise. A small "thinking…" state while the CLI call runs.

### 4.3 Data flow
1. App load → `GET /chapters` + `GET /progress` + `GET /diagram-state` → render dashboard.
2. Open exercise → `GET /exercises/{id}` → editor with starter code.
3. Run → `POST /exercises/{id}/run {code}` → results. On pass, response includes updated
   xp/level/streak + newly unlocked component → animate diagram + stats.
4. Ask → `POST /chat {question, mode, current_exercise_id}` → render answer.

---

## 5. Chapter Content (3 chapters, ~12 exercises each)

Theory for every chapter is written **for a complete backend beginner**: each new term is
defined, each concept gets a "why does a backend care about this" framing and a real-world
analogy, and exercises build on each other.

### Chapter 1 — Python Fundamentals (~12)
Theory covers: what a program is, the Python runtime, values & types, how the computer
stores data, and how this maps to handling request data later.
1. Greeting function (return vs print)
2. Variables & types; type conversion
3. Arithmetic & operators
4. Strings: slicing, methods, f-strings
5. Lists: index, slice, append
6. Dicts: lookup, `.get` with default, update
7. Conditionals / branching
8. Loops & accumulation
9. List comprehensions
10. Functions: args, defaults, `*args/**kwargs`
11. Error handling: `try/except`, raising
12. Tuples & sets (membership, dedup)
- **Mini-capstone:** given a list of dicts (mini "orders"), compute the total — first taste
  of handling structured data like a backend does.

### Chapter 2 — Python Intermediate, Async & Tooling (~12)
Theory covers: why types help in big codebases, modelling data with classes/dataclasses,
modules, and the big one — **why backends are I/O-bound and what async actually solves**
(with a "waiting in line vs taking a ticket" analogy).
1. Type hints on a function
2. Dataclasses: model a `User`
3. Classes & methods (basic OOP)
4. Modules & imports (use a provided module)
5. Advanced comprehensions (dict/set/nested)
6. Generators & `yield`
7. Decorators (a timing/logging decorator)
8. Context managers (`with`)
9. Async basics: `async def` / `await`
10. `asyncio.gather` — run things concurrently
11. Simulated I/O with `asyncio.sleep` — feel why async matters
12. Async error handling + custom exceptions
- **Mini-capstone:** an async function that "fetches" 3 fake resources concurrently and
  aggregates them — foreshadows calling a DB / third-party service.

### Chapter 3 — SQL Fundamentals on Postgres (~12)
Theory covers: what a database is and why backends don't just use files, tables/rows/
columns, primary & foreign keys, and how SQL is "asking questions of your data." Seed
schema is the **TicketPay** domain (`users`, `movies`, `showtimes`, `seats`, `bookings`).
1. `SELECT` columns
2. `WHERE` filtering
3. `ORDER BY` + `LIMIT`
4. `INSERT`
5. `UPDATE`
6. `DELETE`
7. Aggregations: `COUNT`, `SUM`, `AVG`, `GROUP BY`
8. `HAVING`
9. `INNER JOIN` (bookings ↔ users)
10. `LEFT JOIN`
11. Multi-table JOIN (booking → showtime → movie)
12. Subquery: find seats **not** booked for a showtime
- **Mini-capstone:** the "available seats for a given showtime" query — literally the core
  query of the TicketPay capstone.

---

## 6. Setup & Tooling
- `uv` creates the Python 3.12 venv for `backend/` and manages deps.
- **Postgres installed via Homebrew** (`brew install postgresql@16`), runs as a local
  service; the SQL runner connects to it. A one-time seed script creates the practice DB.
- `bun` or `npm` for the Svelte frontend (Vite dev server on 4000).
- Two run commands (documented in README): start backend on 4001, start frontend on 4000.

---

## 7. Out of Scope (YAGNI for now)
- Chapters 4–12 (added later as content files).
- Multi-user / accounts / auth on the dashboard itself (single local user).
- Cloud deploy (localhost only).
- The actual TicketPay capstone app (that's the week-5+ deliverable, separate project).

---

## 8. Risks & Mitigations
| Risk | Mitigation |
|---|---|
| Arbitrary local code execution (Python runner) | subprocess + 5s timeout + temp dir + output cap; localhost single-user only |
| SQL runner mutating shared data | fresh disposable schema per exercise, dropped after |
| Chat = per-message `claude` CLI cost/latency | documented; show "thinking…"; keep prompts tight |
| System Python is 3.9 | `uv` provisions isolated 3.12; system untouched |
| Postgres not installed | `brew install` as a documented setup step |

---

## 9. Build Order (high level — detailed plan follows separately)
1. Scaffold repo (`backend/`, `frontend/`), Postgres install + seed, `uv` env.
2. Backend: content loader + chapters/exercises endpoints + progress store.
3. Backend: Python runner; then SQL runner.
4. Backend: gamification (XP/level/streak/diagram) + chat proxy.
5. Frontend: dashboard + diagram, lesson view, exercise view + editor, chat panel.
6. Author Chapter 1 → 2 → 3 content (theory + ~12 exercises each).
7. End-to-end pass; README run instructions.
