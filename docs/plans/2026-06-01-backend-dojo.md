# Backend Dojo Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a local, playful backend-learning dashboard (FastAPI :4001 + Svelte :4000) where solving in-browser exercises grows an architecture diagram and awards XP, with a context-aware Claude chat.

**Architecture:** Svelte SPA (4000) ⇄ FastAPI (4001). Backend serves chapter content (data files), runs Python submissions in a sandboxed subprocess and SQL submissions against disposable Postgres schemas, persists progress/XP/mistakes in sqlite, and proxies a Claude chat via the `claude` CLI. Chapters are data so 4–12 are addable without code changes.

**Tech Stack:** Python 3.12 (uv), FastAPI, uvicorn, psycopg3, sqlite3, PostgreSQL (Homebrew); Svelte 5, Vite, CodeMirror 6, marked; pytest.

---

## File Structure

```
backend/
├── pyproject.toml                  # uv project, deps
├── app/
│   ├── main.py                     # FastAPI app, CORS, route mounting
│   ├── config.py                   # paths, ports, PG connection string
│   ├── content_loader.py           # read chapter meta/theory/exercises from disk
│   ├── models.py                   # pydantic request/response models
│   ├── progress/
│   │   ├── store.py                # sqlite schema + CRUD
│   │   └── gamification.py         # XP, level, streak, diagram unlock logic
│   ├── runner/
│   │   ├── python_runner.py        # sandboxed python execution + test harness
│   │   └── sql_runner.py           # disposable schema seed + query + compare
│   ├── chat.py                     # build context prompt + spawn `claude -p`
│   ├── diagram.py                  # canonical component list + unlock mapping
│   └── content/                    # CHAPTER DATA (see content tasks)
│       ├── chapter-01-python-fundamentals/{meta.json,theory.md,exercises/*.json}
│       ├── chapter-02-python-intermediate-async/{...}
│       └── chapter-03-sql-fundamentals/{...}
├── seeds/ticketpay.sql             # seed schema+data for SQL exercises
└── tests/                          # pytest

frontend/
├── package.json, vite.config.js, svelte.config.js, index.html
└── src/
    ├── main.js, App.svelte
    ├── lib/api.js                  # fetch wrappers to :4001
    ├── lib/stores.js               # progress/diagram svelte stores
    ├── components/
    │   ├── ArchitectureDiagram.svelte
    │   ├── StatsBar.svelte         # xp/level/streak
    │   ├── ChapterList.svelte
    │   ├── LessonView.svelte       # theory markdown + concept checks
    │   ├── ExerciseView.svelte     # prompt + CodeMirror + run + results
    │   ├── ResultsPanel.svelte
    │   └── ChatPanel.svelte        # tutor/explain toggle
    └── styles/
```

---

## Phase 0 — Environment & Scaffold

### Task 0.1: Install Postgres and verify
**Files:** none (system setup)

- [ ] **Step 1:** Install: `brew install postgresql@16`
- [ ] **Step 2:** Start service: `brew services start postgresql@16`
- [ ] **Step 3:** Verify: `psql postgres -c "SELECT version();"`
  Expected: prints PostgreSQL 16.x. Ensure `psql` is on PATH (`brew link` if needed).
- [ ] **Step 4:** Create the practice DB: `createdb backend_dojo`
- [ ] **Step 5:** Verify connect: `psql backend_dojo -c "\dt"` → "Did not find any relations." (fine)

### Task 0.2: Scaffold backend with uv
**Files:** Create `backend/pyproject.toml`, `backend/app/__init__.py`, `backend/app/main.py`, `backend/app/config.py`

- [ ] **Step 1:** `cd /Users/aniqhaider/projects/backend-dojo/backend && uv init --python 3.12 --no-readme` then add deps:
  `uv add fastapi "uvicorn[standard]" "psycopg[binary]" pytest httpx`
- [ ] **Step 2:** Write `app/config.py`:
```python
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
CONTENT_DIR = BACKEND_DIR / "app" / "content"
SEEDS_DIR = BACKEND_DIR / "seeds"
PROGRESS_DB = BACKEND_DIR / "progress.db"
PG_DSN = "dbname=backend_dojo"
FRONTEND_ORIGIN = "http://localhost:4000"
PORT = 4001
```
- [ ] **Step 3:** Write `app/main.py` (health route + CORS):
```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import FRONTEND_ORIGIN

app = FastAPI(title="Backend Dojo")
app.add_middleware(
    CORSMiddleware, allow_origins=[FRONTEND_ORIGIN],
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"ok": True}
```
- [ ] **Step 4:** Run: `uv run uvicorn app.main:app --port 4001 --reload` then `curl localhost:4001/health` → `{"ok":true}`
- [ ] **Step 5:** Commit: `feat: scaffold FastAPI backend with health check`

### Task 0.3: Scaffold Svelte frontend
**Files:** `frontend/` (Vite Svelte template)

- [ ] **Step 1:** `cd /Users/aniqhaider/projects/backend-dojo && npm create vite@latest frontend -- --template svelte` then `cd frontend && npm install`
- [ ] **Step 2:** Set dev port to 4000 in `vite.config.js`: `server: { port: 4000 }`
- [ ] **Step 3:** `npm install @codemirror/state @codemirror/view @codemirror/lang-python @codemirror/lang-sql codemirror marked`
- [ ] **Step 4:** Run `npm run dev`, open `http://localhost:4000` → default Svelte page renders.
- [ ] **Step 5:** Commit: `feat: scaffold Svelte+Vite frontend on port 4000`

---

## Phase 1 — Progress Store & Gamification (TDD)

### Task 1.1: sqlite progress store
**Files:** Create `app/progress/store.py`, `tests/test_store.py`

- [ ] **Step 1: Failing test** `tests/test_store.py`:
```python
from app.progress.store import ProgressStore

def test_record_and_fetch_solve(tmp_path):
    s = ProgressStore(tmp_path / "p.db")
    s.init_schema()
    s.record_attempt("ch1-ex01", passed=True, code="print(1)")
    p = s.get_exercise("ch1-ex01")
    assert p["status"] == "solved"
    assert p["attempts"] == 1
```
- [ ] **Step 2:** Run `uv run pytest tests/test_store.py -v` → FAIL (module missing).
- [ ] **Step 3:** Implement `store.py` with sqlite tables from spec §3.5 (`exercise_progress`, `mistakes_log`, `stats`, `diagram_state`) and methods: `init_schema()`, `record_attempt(exercise_id, passed, code, error_category=None, detail=None)`, `get_exercise(id)`, `all_progress()`, `log_mistake(...)`, `recent_mistakes(limit)`, `get_stats()`, `set_stats(...)`, `unlock_component(id)`, `unlocked_components()`. On a passing attempt set status `solved` + `solved_at`; on fail append to `mistakes_log`.
- [ ] **Step 4:** Run pytest → PASS.
- [ ] **Step 5:** Commit: `feat: sqlite progress store`

### Task 1.2: XP / level / streak logic
**Files:** Create `app/progress/gamification.py`, `tests/test_gamification.py`

- [ ] **Step 1: Failing tests**:
```python
from app.progress.gamification import level_for_xp, next_streak

def test_level_curve():
    assert level_for_xp(0) == 1
    assert level_for_xp(100) >= 2

def test_streak_same_day_no_double(): 
    assert next_streak(cur=3, last="2026-06-01", today="2026-06-01") == 3
def test_streak_next_day_increments():
    assert next_streak(cur=3, last="2026-06-01", today="2026-06-02") == 4
def test_streak_gap_resets():
    assert next_streak(cur=3, last="2026-06-01", today="2026-06-04") == 1
def test_streak_first_ever():
    assert next_streak(cur=0, last=None, today="2026-06-01") == 1
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement: `level_for_xp(xp)` using cumulative threshold `100 * n*(n-1)/2` (level 1: 0, L2: 100, L3: 300, L4: 600...); `next_streak(cur,last,today)` per rules in spec §3.6 (same day → unchanged; +1 day → cur+1; gap → 1; no prior → 1).
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: xp/level/streak gamification logic`

### Task 1.3: Diagram component mapping
**Files:** Create `app/diagram.py`, `tests/test_diagram.py`

- [ ] **Step 1: Failing test**:
```python
from app.diagram import COMPONENTS, components_to_unlock

def test_first_solve_unlocks_runtime():
    got = components_to_unlock(solved_ids={"ch1-ex01-greeting"}, all_solved_by_ch={1: False,2:False,3:False})
    assert "py-runtime" in got
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `COMPONENTS` (ordered list with id/label/depends per spec §3.7 table) and `components_to_unlock(...)` mapping solved exercise ids + chapter-complete flags → set of component ids.
- [ ] **Step 4:** Run → PASS.
- [ ] **Step 5:** Commit: `feat: architecture diagram unlock mapping`

---

## Phase 2 — Content Loader & Read Endpoints

### Task 2.1: Content loader
**Files:** Create `app/content_loader.py`, `app/models.py`, `tests/test_content_loader.py`, and a **fixture** chapter under `tests/fixtures/content/chapter-99-test/`.

- [ ] **Step 1:** Create fixture: `meta.json` `{"id":"ch99","title":"Test","order":99,"summary":"x"}`, `theory.md` "# Hi", `exercises/01-x.json` (minimal python exercise per spec §3.2, with `tests`).
- [ ] **Step 2: Failing test**:
```python
from app.content_loader import ContentLoader

def test_loads_chapter_and_hides_tests(tmp_path_factory):
    loader = ContentLoader(FIXTURE_CONTENT_DIR)
    chapters = loader.list_chapters()
    assert chapters[0]["title"] == "Test"
    ex = loader.get_exercise_public("ch99-ex01-x")
    assert "tests" not in ex            # hidden tests must never reach client
    full = loader.get_exercise_full("ch99-ex01-x")
    assert "tests" in full
```
- [ ] **Step 3:** Run → FAIL.
- [ ] **Step 4:** Implement loader: scan dirs, parse json/md, `list_chapters()`, `get_chapter(id)` (theory + ordered public exercises), `get_exercise_public(id)` (strips `tests`/`expected_query_result`), `get_exercise_full(id)`. Define pydantic models in `models.py`.
- [ ] **Step 5:** Run → PASS. Commit: `feat: chapter content loader with hidden tests`

### Task 2.2: Read endpoints
**Files:** Modify `app/main.py`; Create `tests/test_read_endpoints.py`

- [ ] **Step 1: Failing test** using FastAPI `TestClient`: GET `/chapters` → 200 list; GET `/chapters/ch99` → theory present; GET `/exercises/ch99-ex01-x` → no `tests` key.
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Add routes wiring `ContentLoader` + `ProgressStore` (merge solved status into chapter/exercise listing). Add `GET /progress` and `GET /diagram-state`.
- [ ] **Step 4:** Run → PASS. Commit: `feat: read endpoints for chapters/exercises/progress`

---

## Phase 3 — Python Runner (TDD)

### Task 3.1: Sandboxed python execution + harness
**Files:** Create `app/runner/python_runner.py`, `tests/test_python_runner.py`

- [ ] **Step 1: Failing tests**:
```python
from app.runner.python_runner import run_python_exercise

EX = {"starter_code":"", "tests":[{"call":"total(2,3)","expect":5}]}

def test_pass():
    r = run_python_exercise("def total(a,b): return a+b", EX)
    assert r["all_passed"] is True
    assert r["results"][0]["passed"] is True

def test_wrong_output():
    r = run_python_exercise("def total(a,b): return 0", EX)
    assert r["all_passed"] is False
    assert r["results"][0]["got"] == "0"

def test_timeout():
    r = run_python_exercise("def total(a,b):\n while True: pass", EX)
    assert r["error_category"] == "timeout"

def test_syntax_error():
    r = run_python_exercise("def total(a,b) return a", EX)
    assert r["error_category"] == "syntax_error"
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement: write user code + generated harness (imports user code, runs each `call` via `eval`/`exec`, prints JSON of results) to a temp file; run `uv run python <file>` via `subprocess.run(timeout=5, capture_output=True)`; parse JSON; categorize errors (`timeout` on `TimeoutExpired`, `syntax_error` on SyntaxError in stderr, `wrong_output` otherwise, `runtime_error` on exception). Cap captured output length.
- [ ] **Step 4:** Run → PASS. Commit: `feat: sandboxed python exercise runner`

---

## Phase 4 — SQL Runner (TDD)

### Task 4.1: Seed file
**Files:** Create `backend/seeds/ticketpay.sql`

- [ ] **Step 1:** Write DDL+INSERTs for `users, movies, showtimes, seats, bookings` with deterministic sample rows (small, known). Use a dedicated schema so it's disposable, e.g. statements run inside `CREATE SCHEMA ex; SET search_path=ex; ...`.
- [ ] **Step 2:** Verify: `psql backend_dojo -f seeds/ticketpay.sql` runs clean; then drop with `DROP SCHEMA ex CASCADE;`.
- [ ] **Step 3:** Commit: `feat: ticketpay SQL seed`

### Task 4.2: SQL runner
**Files:** Create `app/runner/sql_runner.py`, `tests/test_sql_runner.py` (requires local Postgres running)

- [ ] **Step 1: Failing tests**:
```python
from app.runner.sql_runner import run_sql_exercise
EX = {"schema_key":"ticketpay","expected_query_result":None,"order_sensitive":False,
      "starter_code":""}

def test_select_matches_expected():
    ex = {**EX, "expected_query_result":[{"id":1}], }
    r = run_sql_exercise("SELECT id FROM users WHERE id=1;", ex)
    assert r["all_passed"] is True

def test_sql_error_category():
    r = run_sql_exercise("SELEKT * FROM users;", {**EX,"expected_query_result":[]})
    assert r["error_category"] == "sql_error"
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement: connect via psycopg to `PG_DSN`; create a uniquely-named throwaway schema; load the seed for `schema_key` into it (`SET search_path`); run the user query; fetch rows as list[dict]; compare to `expected_query_result` (sort both unless `order_sensitive`); always `DROP SCHEMA ... CASCADE` in `finally`. Categorize psycopg errors as `sql_error`.
- [ ] **Step 4:** Run → PASS. Commit: `feat: postgres SQL exercise runner with disposable schema`

---

## Phase 5 — Run Endpoint (ties runners + gamification)

### Task 5.1: POST /exercises/{id}/run
**Files:** Modify `app/main.py`; Create `tests/test_run_endpoint.py`

- [ ] **Step 1: Failing test:** POST a correct python solution → response `{all_passed:true, awarded_xp:>0, new_components:[...], stats:{...}}`; posting again → `awarded_xp:0` (idempotent XP).
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement: load full exercise, dispatch to python/sql runner by `type`. On pass+first solve: record solve, add xp, recompute level, update streak (using today's date passed in/`date.today()`), compute newly-unlocked components, persist. On fail: `log_mistake` with category. Return results + deltas.
- [ ] **Step 4:** Run → PASS. Commit: `feat: run endpoint with xp/diagram updates`

---

## Phase 6 — Chat Proxy

### Task 6.1: Context builder (TDD) + claude spawn
**Files:** Create `app/chat.py`, `tests/test_chat_context.py`

- [ ] **Step 1: Failing test** for the pure context builder (no CLI):
```python
from app.chat import build_context

def test_context_includes_mistakes_and_exercise():
    ctx = build_context(mode="tutor", question="why fail?",
        current_exercise={"id":"ch1-ex01","prompt_md":"do x"},
        recent_mistakes=[{"exercise_id":"ch1-ex01","error_category":"wrong_output"}],
        solved=["ch1-ex00"])
    assert "wrong_output" in ctx
    assert "do x" in ctx
```
- [ ] **Step 2:** Run → FAIL.
- [ ] **Step 3:** Implement `build_context(...)` → a single string with sections (current exercise, solved list, recent mistakes, the question). Implement `system_prompt_for(mode)` → Tutor (Socratic, never give full exercise solutions, cite his past mistakes) vs Explain (direct). Implement `ask_claude(question, mode, context)` that runs `subprocess.run(["claude","-p", context, "--append-system-prompt", system_prompt_for(mode)], timeout=120, capture_output=True, text=True)` and returns stdout. **Verify exact CLI flags** with `claude -p "hi" --append-system-prompt "be terse"` during this task; adjust if the flag name differs.
- [ ] **Step 4:** Run context test → PASS. Manual: hit the spawn once to confirm a real answer returns.
- [ ] **Step 5:** Commit: `feat: claude chat context builder + CLI proxy`

### Task 6.2: POST /chat endpoint
**Files:** Modify `app/main.py`

- [ ] **Step 1:** Add `POST /chat` that pulls current exercise + recent mistakes + solved from the store, builds context, calls `ask_claude`, returns `{answer}`. (No test that spawns CLI in CI; manual verify.)
- [ ] **Step 2:** Manual: `curl -XPOST localhost:4001/chat -d '{"question":"what is a list?","mode":"explain"}' -H 'content-type: application/json'` → returns text.
- [ ] **Step 3:** Commit: `feat: /chat endpoint`

---

## Phase 7 — Frontend

### Task 7.1: API client + stores
**Files:** Create `src/lib/api.js`, `src/lib/stores.js`
- [ ] **Step 1:** `api.js`: `getChapters, getChapter(id), getExercise(id), runExercise(id, code), getProgress, getDiagram, chat(question,mode,exId)` — all fetch to `http://localhost:4001`.
- [ ] **Step 2:** `stores.js`: writable stores `progress`, `diagram`, `currentExercise`.
- [ ] **Step 3:** Commit: `feat: frontend api client + stores`

### Task 7.2: Dashboard shell — StatsBar + ChapterList + ArchitectureDiagram
**Files:** Create the three components + wire in `App.svelte`
- [ ] **Step 1:** `StatsBar.svelte` shows xp, level, streak from `progress` store.
- [ ] **Step 2:** `ArchitectureDiagram.svelte`: an SVG with all `COMPONENTS` positioned; unlocked ones full-opacity + animated-in (CSS transition on a `unlocked` class), locked ones dimmed. Layout left→right: client → handler/router → db, with the `db-connection` edge appearing last.
- [ ] **Step 3:** `ChapterList.svelte`: chapters with completion rings + drill into exercises.
- [ ] **Step 4:** Verify in browser against a backend with some seeded progress: stats + diagram render.
- [ ] **Step 5:** Commit: `feat: dashboard shell with stats, chapter list, growing diagram`

### Task 7.3: LessonView (theory)
**Files:** Create `src/components/LessonView.svelte`
- [ ] **Step 1:** Fetch chapter, render `theory.md` via `marked` (sanitize), show exercise list sidebar with solved markers.
- [ ] **Step 2:** Verify a chapter's theory renders.
- [ ] **Step 3:** Commit: `feat: lesson/theory view`

### Task 7.4: ExerciseView + editor + results
**Files:** Create `ExerciseView.svelte`, `ResultsPanel.svelte`
- [ ] **Step 1:** CodeMirror editor (python or sql mode by exercise `type`), prefilled `starter_code`, Run button → `runExercise`.
- [ ] **Step 2:** `ResultsPanel` shows per-test passed/expected/got or the error.
- [ ] **Step 3:** On `all_passed`: success animation, refresh `progress`+`diagram` stores → diagram animates the `new_components`, XP pops.
- [ ] **Step 4:** Verify end-to-end: solve a real exercise, watch diagram grow.
- [ ] **Step 5:** Commit: `feat: exercise view with editor, runner results, diagram growth`

### Task 7.5: ChatPanel
**Files:** Create `src/components/ChatPanel.svelte`
- [ ] **Step 1:** Dockable panel, Tutor⇄Explain toggle, message thread, sends current exercise id; "thinking…" while awaiting.
- [ ] **Step 2:** Verify a question returns a tailored answer.
- [ ] **Step 3:** Commit: `feat: context-aware chat panel`

---

## Phase 8 — Content Authoring

> Author content as data files. For each exercise use the JSON shape in spec §3.2.
> Theory must be **beginner-first**: define every term, explain *why a backend cares*,
> use a concrete analogy, keep paragraphs short. Each chapter ~12 exercises + mini-capstone.

### Task 8.1: Chapter 1 — Python Fundamentals
**Files:** `app/content/chapter-01-python-fundamentals/{meta.json,theory.md,exercises/01..13.json}`
- [ ] **Step 1:** Write `theory.md` (what a program is, the Python runtime, values/types, how this maps to handling request data later).
- [ ] **Step 2:** Write the 12 exercises + mini-capstone from spec §5 Ch1, each with starter_code, ≥2 tests, hints, xp, concept_tags. Map exercises→diagram components in `meta.json`.
- [ ] **Step 3:** Verify: each exercise's reference solution passes via the run endpoint.
- [ ] **Step 4:** Commit: `content: chapter 1 python fundamentals`

### Task 8.2: Chapter 2 — Python Intermediate, Async & Tooling
**Files:** `app/content/chapter-02-python-intermediate-async/{...}`
- [ ] **Step 1:** Write `theory.md` (why types help, dataclasses, modules, and **why backends are I/O-bound + what async solves** with the queue analogy).
- [ ] **Step 2:** Write 12 exercises + async mini-capstone from spec §5 Ch2. For async exercises the test harness must `asyncio.run` the call.
- [ ] **Step 3:** Verify reference solutions pass.
- [ ] **Step 4:** Commit: `content: chapter 2 intermediate + async`

### Task 8.3: Chapter 3 — SQL Fundamentals on Postgres
**Files:** `app/content/chapter-03-sql-fundamentals/{...}`
- [ ] **Step 1:** Write `theory.md` (what a database is + why not files, tables/rows/columns, PK/FK, SQL as "asking questions").
- [ ] **Step 2:** Write 12 SQL exercises + the "available seats" mini-capstone from spec §5 Ch3, each with `expected_query_result` computed against the seed.
- [ ] **Step 3:** Verify each reference query matches expected via the run endpoint.
- [ ] **Step 4:** Commit: `content: chapter 3 sql fundamentals`

---

## Phase 9 — Integration & Docs

### Task 9.1: README + run scripts
**Files:** Create `README.md`, `scripts/dev.sh`
- [ ] **Step 1:** README: prerequisites (brew postgres, uv, node), one-time setup, how to start backend (`uv run uvicorn app.main:app --port 4001`) and frontend (`npm run dev`).
- [ ] **Step 2:** `scripts/dev.sh` starts both.
- [ ] **Step 3:** Commit: `docs: readme + dev script`

### Task 9.2: Full end-to-end smoke
- [ ] **Step 1:** Fresh `progress.db`; open dashboard; complete Ch1 ex1 → diagram unlocks `py-runtime`; ask the chat a question in Tutor mode about a failed attempt → it references the mistake.
- [ ] **Step 2:** Complete one SQL exercise → `postgres-db` unlocks.
- [ ] **Step 3:** Commit any fixups.

---

## Self-Review Notes
- **Spec coverage:** §3.2 content shape → Task 2.1/8.x; §3.3 python runner → Phase 3; §3.4 SQL runner → Phase 4; §3.5 store → 1.1; §3.6 gamification → 1.2/5.1; §3.7 diagram → 1.3/7.2; §3.8 chat → Phase 6; §3.9 endpoints → 2.2/5.1/6.2; §4 frontend → Phase 7; §5 content → Phase 8; §6 setup → 0.1/9.1. No gaps.
- **Deferred-but-resolved:** exact `claude` CLI flags resolved in Task 6.1; XP curve made concrete in Task 1.2.
- **Type consistency:** runner outputs use `all_passed`, `results[].{passed,expected,got}`, `error_category` consistently across Phases 3–5 and frontend 7.4.
```
