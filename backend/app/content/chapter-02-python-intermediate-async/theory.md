# Python Intermediate, Async & Tooling

You already know Python's basics. Now we'll add the tools that backend code actually leans on every day: type hints, classes/dataclasses, a handful of "Pythonic" patterns, and the big one — **async**. Wherever it helps, I'll relate things back to JavaScript/TypeScript, which you already know well.

## Why type hints matter (vs JS/TS)

In plain JavaScript, a function argument can be anything — a string, a number, an object — and you only find out it was wrong when something explodes at runtime. That's why your team reached for **TypeScript**: it lets you *annotate* shapes and catches mismatches before you ship.

Python has the same idea, called **type hints**:

```python
def double(n: int) -> int:
    return n * 2
```

The `: int` says "this argument should be an integer" and `-> int` says "this returns an integer". A **term to know**: a *type hint* is metadata describing the expected type of a variable, argument, or return value.

[[exercise:ch2-ex01-typehints]]

Here's the twist that surprises TS developers: **Python does not enforce type hints at runtime.** They're documentation plus a signal for tools. A separate type-checker (like `mypy` or `pyright`) reads them and flags mistakes — exactly like `tsc` does for you. The Python interpreter itself ignores them and runs the code anyway.

Why does a backend care? Because a backend is a contract machine. Request comes in, response goes out, and a hundred functions pass data between them. Type hints make those contracts explicit, so a teammate (or you, six months later) can see what a function expects without reading its body. Frameworks like **FastAPI** go further: they *read* your type hints to validate incoming JSON and auto-generate API docs. Hints stop being optional comments and become the source of truth.

## Modeling data: classes & dataclasses

A **class** is a blueprint for objects that bundle data (attributes) with behavior (methods). If you've written a JS `class`, this is the same concept:

```python
class Counter:
    def __init__(self):
        self.value = 0
    def inc(self):
        self.value += 1
```

`__init__` is the constructor (like `constructor()` in JS), and `self` is Python's explicit version of `this` — except you have to write it out as the first parameter of every method. To use a class, you *instantiate* it (`c = Counter()`) and then call its methods (`c.inc()`).

[[exercise:ch2-ex03-class]]

Often, though, you just want a plain bag of typed data — no real behavior. Writing a full class with an `__init__` that copies every argument onto `self` is tedious boilerplate. That's what a **dataclass** solves:

```python
from dataclasses import dataclass

@dataclass
class User:
    name: str
    age: int
```

That `@dataclass` line is a **decorator** (more on those below). It auto-generates the constructor, a readable `__repr__`, and equality comparison. Mentally, it's the closest Python gets to a TypeScript `interface` *plus* a constructor in one declaration. Backends use dataclasses constantly to model domain objects: a `User`, an `Order`, a `CartItem`. You build one by calling it like a function (`u = User("Asha", 30)`) and read fields with dot access (`u.name`).

[[exercise:ch2-ex02-dataclass]]

### Reusing the standard library

You rarely write everything yourself. Python ships with a huge **standard library** of ready-made modules you pull in with `import`. For example, `import math` gives you `math.pi` and a pile of math helpers; the built-in `round(value, 2)` rounds to a given number of decimal places. This is the same idea as `import` in JS/TS, except many batteries come bundled.

[[exercise:ch2-ex04-modules]]

## Comprehensions, generators, decorators, context managers (the Pythonic toolkit)

These four patterns show up everywhere in idiomatic Python.

**Comprehensions** are compact loops that build a collection. Instead of `for`-pushing into a list, you write the result inline — think `Array.map`/`filter` but baked into the language:

```python
lengths = {word: len(word) for word in words}   # a dict comprehension
```

[[exercise:ch2-ex05-comprehensions]]

**Generators** produce values lazily, one at a time, instead of building a whole list in memory. A function with `yield` is a generator:

```python
def squares(n):
    for i in range(n):
        yield i * i
```

It's like a JS generator (`function*` / `yield`). Why a backend cares: streaming a million database rows through a generator uses near-constant memory, whereas loading them all into a list could crash the process. When you actually want a concrete list, wrap the generator in `list(...)` to pull every value out at once.

[[exercise:ch2-ex06-generators]]

**Decorators** are functions that wrap other functions to add behavior — without editing the original. The `@something` syntax is just `func = something(func)`:

```python
def double_result(fn):
    def wrapper(*args, **kwargs):
        return fn(*args, **kwargs) * 2
    return wrapper
```

Backends use decorators for cross-cutting concerns: `@app.get("/users")` registers a route, `@login_required` guards an endpoint. Conceptually similar to React higher-order components or middleware. The `*args, **kwargs` in the wrapper just means "accept whatever arguments the original took and forward them on".

[[exercise:ch2-ex07-decorators]]

**Context managers** guarantee setup/teardown around a block using `with`. They ensure cleanup runs even if an error happens:

```python
with open("file.txt") as f:
    data = f.read()
# file is automatically closed here, even on error
```

This is huge for backends: opening files, acquiring database connections, or grabbing a lock — all need reliable release. `with` is your "always run the cleanup" guarantee (like `try/finally`, but tidier). The same `with` works on any file-like object — for example `io.StringIO(text)` gives you an in-memory text stream you can loop over line by line (`for line in f:`) without touching the disk.

[[exercise:ch2-ex08-context-manager]]

## The big one: why backends are I/O-bound and what async solves

Here's the core insight: a backend spends most of its time **waiting**. Waiting on the database, waiting on a third-party API, waiting on disk. Actual CPU work is tiny by comparison. We say such work is **I/O-bound** (I/O = input/output) — bottlenecked by waiting, not computing.

**Analogy.** Imagine a coffee shop with one barista (your single thread). In the *synchronous* model, the barista takes your order, then stands frozen staring at the espresso machine for two minutes while it brews — ignoring everyone else in line. That's blocking: one slow request stalls the whole queue.

The *async* model is **take-a-ticket**: the barista starts your espresso, hands the *next* customer a ticket, takes their order too, and circles back to whichever drink is ready. One worker, many in-flight orders, because the waiting overlaps. That's exactly what async does: while one request waits on the database, the server handles other requests.

You already know this model from JavaScript! Node is single-threaded and uses `async`/`await` over Promises for the same reason. Python's version looks almost identical:

```python
import asyncio

async def get_value():        # 'async def' = a coroutine
    await asyncio.sleep(0)     # 'await' = pause here, let others run
    return 42
```

A **term to know**: an `async def` function is a *coroutine* — calling it doesn't run it, it returns an awaitable object (like a JS Promise). You `await` it to get the result. `asyncio` is Python's built-in event loop that schedules these coroutines.

[[exercise:ch2-ex09-async-basics]]

That `await asyncio.sleep(...)` line above is worth dwelling on: `asyncio.sleep` is the standard stand-in for "waiting on I/O" (a database, a network call). It pauses *this* coroutine at the `await` and lets the event loop run others in the meantime — exactly the overlap that makes a backend fast. Even `asyncio.sleep(0)` creates a real await point that yields control.

[[exercise:ch2-ex11-async-sleep]]

To run things **concurrently**, use `asyncio.gather` — the close cousin of `Promise.all`:

```python
results = await asyncio.gather(fetch_user(), fetch_orders(), fetch_count())
```

All three start, their waiting overlaps, and you get the results as a list once all finish. In a real backend, `fetch_user` and `fetch_orders` might be two separate database queries — running them concurrently can cut your endpoint's latency dramatically.

[[exercise:ch2-ex10-async-gather]]

### Errors in async code

`try`/`except` works inside coroutines exactly as it does in normal functions: wrap the risky line, and catch the specific error type you expect. For example, `int("x")` raises a `ValueError`, so `try: return int(s) / except ValueError: return -1` turns a crash into a safe fallback. You can also define your **own** exception types by subclassing `Exception` (`class ValidationError(Exception): pass`) — backends use these to signal domain problems like bad input.

[[exercise:ch2-ex12-async-errors]]

One caution: async only helps with *waiting* (I/O). It does **not** speed up heavy CPU number-crunching — for that you need multiple processes. But since backends are overwhelmingly I/O-bound, async is the right default. Put it all together and a single endpoint can fan out several awaits with one `gather`, then assemble the results into the response dict it returns.

[[exercise:ch2-ex13-capstone]]

## Tooling: uv and ruff

Two modern tools you'll see in this course and in real projects:

**uv** is an extremely fast package manager and virtual-environment tool — think "npm/pnpm for Python", but written in Rust and noticeably faster. It installs dependencies and manages the isolated environment your project runs in, so your packages don't collide with the system Python.

**ruff** is a linter and formatter — "ESLint + Prettier for Python" in a single fast binary. It catches mistakes (unused imports, undefined names) and auto-formats your code to a consistent style. Run it before committing and your reviewers will love you.

That's the toolkit. Next chapter we'll point all of this at a real web framework.
