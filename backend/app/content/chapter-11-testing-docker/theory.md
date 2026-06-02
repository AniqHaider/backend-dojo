# Testing, Docker & Observability

You already trust some of this without naming it. When you ship a React component, you probably have a test that renders it and clicks a button, a CI pipeline that turns red when something breaks, and maybe a Storybook to eyeball it. Backend work uses the exact same instincts — just pointed at functions, databases, and HTTP endpoints instead of the DOM. This chapter connects those familiar instincts to the backend toolbox.

## Why tests (confidence to change code)

The number one reason to write tests is not "correctness" in the abstract — it is **the confidence to change code later**. Software that has no tests becomes software nobody dares to touch. Every edit is a gamble, so features slow down and bugs pile up.

Think about the last time you refactored a tangled component. If it had a solid test suite, you could rip out the internals, run the tests, and *know* in seconds whether you broke anything. If it had no tests, you clicked around manually, hoped you covered every case, and shipped with a knot in your stomach. Backend tests give you that same fast feedback loop for code that has no UI to click.

Tests also serve as **executable documentation**. A test named `test_redact_email_replaces_at_tokens` tells the next engineer exactly what the function is supposed to do — and unlike a comment, it cannot silently go out of date, because CI will fail the moment behavior drifts from the test.

A useful mental model: a test is a tiny program that *uses* your code the way a real caller would, then asserts the result is what you expect. If the assertion holds, the test passes. If not, you get a precise failure message pointing at the gap.

## Unit vs integration tests; the arrange-act-assert shape

Tests come in layers. The two you will write most are:

- **Unit tests** exercise one small piece of logic in isolation — a single function, with no database, no network, no filesystem. They are fast (milliseconds) and pinpoint failures precisely. Your frontend analogy is a pure-function test or a shallow-rendered component test with everything mocked.
- **Integration tests** exercise several pieces working *together*, crossing a real boundary — they actually hit a database, call a real HTTP endpoint, or read a file. They are slower and a bit flakier, but they catch the bugs unit tests miss: wrong SQL, mismatched serialization, broken wiring between layers. The frontend analogy is an end-to-end Cypress/Playwright test that drives a real browser against a running app.

A common rule of thumb is the *test pyramid*: many fast unit tests at the bottom, fewer integration tests in the middle, and a handful of slow end-to-end tests at the top.

Almost every good test follows the **Arrange-Act-Assert** shape:

1. **Arrange** — set up the inputs and any state (build the data, create the user, point at the test DB).
2. **Act** — call the thing under test exactly once.
3. **Assert** — check that the output, or the resulting state, matches what you expect.

Keeping these three phases visually separate makes tests readable and makes failures easy to diagnose.

## pytest basics (test functions, assert, fixtures)

In Python, the dominant test runner is **pytest**. It is refreshingly simple compared to some frontend frameworks:

- A test is just a **function whose name starts with `test_`**, in a file named `test_*.py`. No special class or wrapper required.
- You check expectations with the plain `assert` keyword — `assert add(2, 3) == 5`. pytest rewrites the assertion under the hood so that when it fails you get a rich message showing both sides, not just "AssertionError".

```python
def test_add_two_numbers():
    # Arrange
    a, b = 2, 3
    # Act
    result = add(a, b)
    # Assert
    assert result == 5
```

Run the whole suite with `pytest`. It discovers your test files, runs every `test_` function, and prints a green dot per pass or a detailed traceback per failure.

When several tests need the same setup — a database connection, a sample user, a temp directory — you use a **fixture**. A fixture is a function decorated with `@pytest.fixture` that produces a reusable piece of setup; any test that lists the fixture name as a parameter receives it. This is pytest's version of `beforeEach` in Jest, but more composable: fixtures can depend on other fixtures, and they can clean up after themselves with `yield`.

```python
@pytest.fixture
def sample_user():
    return {"name": "Ada", "active": True}

def test_user_is_active(sample_user):
    assert sample_user["active"] is True
```

You will also lean on **parametrization** (`@pytest.mark.parametrize`) to run the same test body across many input/expected pairs — perfect for edge-case tables like palindrome checks.

## Docker: shipping a consistent environment

"It works on my machine" is the oldest excuse in software. **Docker** kills it. A Docker *image* is a self-contained snapshot of your app *plus* its entire environment — the OS libraries, the exact Python version, the installed dependencies, and your code. A running copy of that image is a *container*.

Because the image bundles everything, the container behaves identically on your laptop, your teammate's laptop, the CI runner, and the production server. No more "but I have Python 3.11 and prod has 3.9". You define the image with a `Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Each line is a layer; Docker caches them, so rebuilds are fast when only your code changed. `docker build -t myapi .` produces the image; `docker run -p 8000:8000 myapi` starts a container. The frontend parallel is shipping a locked `package-lock.json` plus a known Node version — Docker just takes that idea all the way down to the operating system. When you need several services together (your API, a Postgres database, Redis), `docker-compose` wires them into one reproducible stack with a single `docker compose up`.

## Observability: logs, metrics, traces & health checks

Once your service runs in production where you cannot attach a debugger, you need to *observe* it from the outside. Observability rests on **three pillars**:

- **Logs** — timestamped text records of discrete events ("user 42 logged in", "payment failed: card declined"). Like `console.log`, but structured (often JSON) and centralized so you can search across all instances. Each log line carries a **level** — `DEBUG`, `INFO`, `WARNING`, `ERROR` — so you can filter noise from alarms.
- **Metrics** — numeric measurements aggregated over time: requests per second, error rate, p95 latency, memory usage. These power dashboards and alerts ("page me if error rate > 1%"). Think of them as the Web Vitals of your backend.
- **Traces** — the path of a single request as it hops through multiple services, with timing at each step. When one request is slow, a trace shows you *which* hop ate the time — the backend cousin of the browser performance/network waterfall.

A close companion is the **health check**: a tiny endpoint (commonly `/health` or `/healthz`) that returns `200 OK` when the service and its critical dependencies are alive. Load balancers and orchestrators poll it constantly; if it stops returning healthy, traffic is routed away or the container is restarted. A good health check reports not just "I'm up" but *which* dependency is failing, so on-call engineers know where to look.

Put together: tests give you confidence to change code, Docker guarantees the code runs the same everywhere, and observability tells you what that code is actually doing once real users hit it. These three habits are what separate a hobby script from a production backend service.
