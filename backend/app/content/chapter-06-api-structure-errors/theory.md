# API Structure, Validation & Errors

You already know how to ship a frontend: components, state, a design system, and error boundaries. A backend API has the same need for structure and discipline — just on the other side of the wire. This chapter is about keeping an API **organized**, **defensive**, and **predictable**.

## Structuring an API project (routers, models, services)

When a frontend grows, you don't put every component in one file — you split by feature and by responsibility (components, hooks, utils). A backend uses the same instinct, usually in three layers:

- **Routers** (also called controllers or route handlers) — the thin layer that maps a URL + HTTP method to a function. Think of these like your page/route components: they read the request, call something, and return a response. They should contain *almost no business logic*.
- **Models / schemas** — the shape of your data. There are usually two flavors: **database models** (how a row is stored, e.g. a SQLAlchemy table) and **request/response schemas** (what the API accepts and returns, e.g. a Pydantic model). This is the backend equivalent of your TypeScript types and form-validation schemas.
- **Services** — the "business logic" layer. "Book a seat if it's free, otherwise reject" lives here. Services don't know about HTTP at all; they just take inputs and return results or raise errors. This is like extracting logic out of a component into a plain function so it's testable and reusable.

**Why bother?** The same reason you don't write a 2,000-line component: separation of concerns. A router that only does HTTP plumbing, a service you can unit-test without a web server, and models you can reuse everywhere. When a bug appears, you know which layer to open.

A common request lifecycle: `Router` receives the request → validates input against a **schema** → calls a **service** → service talks to **models/DB** → returns data → router wraps it in a response. Errors raised anywhere bubble up to a single handler.

## Validation: never trust the client

Your frontend already validates forms — required fields, email format, max length. So why validate *again* on the backend?

**Because the client is not trustworthy.** Anyone can bypass your UI: a `curl` command, Postman, a script, a malicious actor, or simply an old mobile app version that predates your latest rule. Frontend validation is a **UX feature** (fast feedback, fewer round-trips). Backend validation is a **correctness and security boundary**. They serve different goals, so you need both.

Treat every incoming request as potentially hostile or malformed. Validate:

- **Presence** — are all required fields there? (`validate(payload, required)` in this chapter)
- **Type** — is `age` actually a number, not the string `"twelve"`?
- **Shape/format** — does the email look like an email? Is the enum value one you allow?
- **Range/limits** — clamp a page size to a sane maximum so nobody requests 10 million rows.

Frameworks like FastAPI do a lot of this for you via Pydantic models: declare the shape once, and malformed requests are rejected automatically before your code runs. But the *principle* — never trust the client — is yours to own.

## Error handling & consistent error shapes

On the frontend, an unhandled exception might just blank a component. On a backend, an unhandled exception leaks a stack trace, returns a vague 500, and gives your frontend nothing useful to display.

The fix is a **consistent error envelope** — every response, success or failure, has the same predictable shape:

```json
{ "ok": true,  "data": { ... } }
{ "ok": false, "error": "Seat already booked" }
```

(See the `envelope(ok, data)` exercise.) Why is this worth it? Because the *consumer* — your own frontend — can write **one** response handler instead of guessing the shape per endpoint. Check `ok`, branch once, done. It's the same reason a design system beats bespoke buttons everywhere: predictability scales.

Internally, services should **raise** errors (e.g. `raise PermissionError(...)`) rather than returning ad-hoc dictionaries. A single central handler then maps each error type to a status code and a clean envelope. That mapping (`error_to_status` in this chapter) is the glue between "something went wrong in business logic" and "what the HTTP layer tells the client."

## HTTP status codes for errors (400/401/403/404/422/500)

Status codes are a contract. The frontend reads them to decide what to do (retry? redirect to login? show a field error?). The ones you'll use constantly:

- **400 Bad Request** — the request is malformed or nonsensical (bad JSON, wrong type). "I can't even parse what you sent."
- **401 Unauthorized** — you are **not authenticated**. We don't know who you are. (Misnamed historically; it really means "unauthenticated.") Fix: log in / send a token.
- **403 Forbidden** — we know who you are, but you're **not allowed** to do this. Fix: nothing the user can do; they lack permission.
- **404 Not Found** — the resource doesn't exist (or we're pretending it doesn't, to hide it).
- **422 Unprocessable Entity** — the JSON was well-formed and parsed fine, but a **field failed a business/validation rule** (e.g. email is missing the `@`, age is negative). This is the "validation failed" code FastAPI returns by default.
- **500 Internal Server Error** — *we* broke, not you. An unexpected exception. The client can't fix this; it's a signal for your logs and alerts.

Quick mental model: **4xx = the caller's fault, 5xx = the server's fault.** 400 vs 422 trips people up: 400 means "I couldn't understand the request at all," while 422 means "I understood it perfectly, but the values don't satisfy the rules."

## Schema migrations (evolving the DB safely)

Your database schema — the tables and columns — will change over time. You'll add a `phone` column, rename a field, add an index. On the frontend you'd just edit a type and redeploy. A database is different: it holds **existing data** you can't lose.

A **migration** is a small, ordered, version-controlled script that describes a change to the schema (e.g. "add column `phone` to `users`"). Tools like **Alembic** (for SQLAlchemy) generate and run these. Each migration has an "up" (apply) and ideally a "down" (undo).

**Why version your schema instead of editing tables by hand?**

- **Reproducibility** — every environment (your laptop, staging, production, a teammate's machine) reaches the *same* schema by running the same ordered scripts. Like committing code instead of pasting snippets in chat.
- **History & review** — migrations live in git. You can see when `phone` was added, by whom, and review it in a PR.
- **Safety & rollback** — applying changes in controlled steps (and being able to reverse them) beats a risky manual `ALTER TABLE` on a live production database holding real customer rows.
- **Coordination** — in a team, hand-edited databases drift apart. Migrations keep everyone in lockstep.

The analogy: migrations are to your database what git history is to your code — an auditable, replayable sequence of changes that any environment can fast-forward to. Never edit production tables by hand; write a migration, review it, run it.

---

**Recap:** Split your API into routers/models/services so each layer has one job. Validate everything from the client because the client lies. Raise typed errors and map them to a consistent envelope and the correct status code. And evolve your schema through reviewable, replayable migrations rather than manual edits.
