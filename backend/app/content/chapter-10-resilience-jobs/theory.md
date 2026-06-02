# Background Jobs & Resilience

As a frontend engineer you already know one golden rule: never block the UI thread. If you run an expensive loop on the main thread, the page freezes, clicks stop responding, and users rage-quit. Backends have the exact same rule, just one layer down: **never block the request.** This chapter is about what to do when a request needs to perform slow work, and what to do when that work depends on another service that is flaky, slow, or briefly down.

We will keep coming back to one concrete example: **an HTTP endpoint that has to charge a customer through a third-party payment API and then send them a confirmation email.** Both of those steps talk to systems you do not control, and both can fail or hang. This is exactly the "flaky third-party service" problem.

## Synchronous vs asynchronous work (why not do everything in the request)

A **synchronous** request does everything before it replies. The browser calls `POST /checkout`, your handler charges the card, sends the email, writes to the database, and only then returns `200 OK`. Simple to reason about — but fragile.

Think about the timing. The payment API normally answers in 300ms but occasionally takes 8 seconds. Sending email takes another second. If you do it all inline, your user stares at a spinner for 9 seconds, and your web server has a worker tied up the whole time doing nothing but waiting. Under load, all your workers end up blocked waiting on a slow third party, and your *entire* site stops responding — even pages that have nothing to do with payments. One slow dependency takes down everything.

There is also a correctness trap. Suppose the charge succeeds but the email send throws. Do you return an error? The user thinks checkout failed and tries again — now they get charged twice. Cramming several risky operations into one request makes "what state are we in if step 3 fails?" very hard to answer.

The fix is **asynchronous work**: do the minimum needed to answer the user *right now*, and push the slow/risky parts into the background to run later. The request becomes "record that this checkout should happen, enqueue the work, return fast." The user gets a quick response; the heavy lifting happens out of band.

## Message queues & background workers

The standard tool for "do this later" is a **message queue** (RabbitMQ, AWS SQS, Redis-backed queues like those behind Celery or BullMQ). The pattern has two sides:

- A **producer** (your web request handler) puts a small message — a *job* — onto the queue. A job is just data: `{"type": "charge_and_email", "order_id": 1234}`. This is fast: write to the queue, return.
- A **worker** (a separate long-running process) pulls jobs off the queue and actually does the work — calls the payment API, sends the email.

This decoupling is the whole point. The web server's job is to be responsive; the worker's job is to grind through slow work. You can run many workers to process jobs in parallel, and scale them independently from your web tier. If 10,000 checkouts arrive in a spike, they pile up safely in the queue and workers drain them at a sustainable rate instead of melting your payment integration.

It is the same mental model as a frontend message bus or a task queue you might post work onto — fire the event, let a listener handle it later — but durable and across process/machine boundaries.

## At-least-once delivery → idempotent consumers

Here is a subtlety that trips up everyone new to queues. Most queues guarantee **at-least-once delivery**, not exactly-once. That means: a job will be delivered *at least* one time, but occasionally the *same* job is delivered *twice*. Why? Imagine a worker pulls a job, finishes the work, but crashes (or its network blips) right before it tells the queue "done." The queue never got the acknowledgment, so it assumes the job was lost and hands it to another worker. The work runs again.

If your job is "charge the customer $50," running it twice means charging $100. Bad.

The cure is to make your worker **idempotent**: running the same job twice produces the same end state as running it once. Practical techniques:

- Use a unique key (e.g. the `order_id` or a generated `idempotency_key`) and record "I already processed this." Before doing the work, check: have I seen this key? If yes, skip.
- Ask the third party to dedupe for you. Good payment APIs accept an `Idempotency-Key` header — send the same key on a retry and they return the original result instead of charging again.

Idempotency is not optional decoration; with at-least-once queues it is a *requirement* for correctness. (Exercise 06 models exactly this "skip if already done" worker.)

## Retries with exponential backoff (+ jitter)

The payment API just returned `503 Service Unavailable`. It is probably a transient hiccup — overloaded for a moment. The right move is usually to **retry**, not to give up. But naive retries make things worse.

If the service is struggling and every client instantly retries in a tight loop, you slam it with even *more* traffic and keep it down — a self-inflicted denial of service. So we space retries out and grow the gap each time: **exponential backoff.** Wait 1s, then 2s, then 4s, then 8s. Each attempt doubles the delay (`delay = base * 2 ** attempt`), giving the dependency room to recover. (Exercises 01 and 02 implement this, including a cap so you do not wait absurdly long.)

Two important refinements:

- **Cap the delay.** Without a ceiling, doubling reaches minutes. Clamp it: `min(cap, base * 2 ** attempt)`.
- **Add jitter.** If a thousand clients all failed at the same instant and all back off by exactly 1s, 2s, 4s..., they retry in synchronized waves — a "thundering herd." Adding a small random amount to each delay spreads them out.

And know **what** to retry. Retry on transient errors: timeouts, `429 Too Many Requests`, and `5xx` server errors. Do *not* retry on `4xx` client errors like `400` or `404` — those mean *you* sent something wrong, and retrying will fail identically forever. (Exercise 03 encodes this rule.) Always cap the number of attempts so a request cannot retry endlessly.

## Circuit breakers & timeouts

Retries handle a brief blip. But what if the payment provider is hard down for ten minutes? Retrying every request — even with backoff — wastes resources, ties up workers waiting, and delays the inevitable failure your user is going to see anyway.

A **circuit breaker** is a guard that watches recent calls and trips when failures pile up. It has three states, modeled on an electrical breaker:

- **Closed** — normal. Calls flow through. Count failures.
- **Open** — too many recent failures (failures ≥ a threshold). *Stop calling* the dead service entirely for a cooldown period and **fail fast** — return an error immediately instead of waiting on a doomed call. This protects both you (workers stay free) and them (you stop hammering a service that is already on the floor).
- **Half-open** — after the cooldown, let a *single* trial call through. If it succeeds, close the breaker (recovered). If it fails, open again and wait more.

(Exercises 04 and 05 model the closed/open/half-open decision logic.)

A circuit breaker only works if calls actually *fail* in a bounded time, which is why every outbound call needs a **timeout**. Never make a network call without one. A call with no timeout can hang for minutes, and a hung call is worse than a failed one — it holds a worker hostage and never gives the breaker a failure to count. Set an explicit deadline (e.g. 2 seconds); if it is exceeded, treat it as a failure and move on. (Exercise 08 models the timeout decision.)

Together: **timeout → retry with backoff → circuit breaker.** Timeouts bound each attempt, backoff spaces out retries of transient failures, and the breaker cuts off a sustained outage so it does not drag down everything else. This trio is the standard answer to "the third-party API is flaky."

## Dead-letter queues

Some jobs just will not succeed. The payment is permanently declined, the data is malformed, or you exhausted all retries. You do not want a poison job retrying forever and clogging the queue, but you also must not silently drop it — that is lost money or lost work no one notices.

The answer is a **dead-letter queue (DLQ)**: a separate queue where you park jobs that failed terminally. After N failed attempts, the job is moved to the DLQ instead of being retried again. Now the main queue keeps flowing, and a human (or an alert) can inspect the DLQ later, fix the underlying issue, and replay those jobs. It is your safety net for "we tried everything and it still failed" — the failure is *captured*, not lost. (Exercise 07 splits results into succeeded vs failed, the core idea behind routing failures to a DLQ.)

Put it all together and the flaky-payment endpoint becomes robust: the request enqueues a job and returns instantly; an idempotent worker processes it with a timeout, retries transient failures with capped backoff, trips a circuit breaker during a sustained outage, and dead-letters anything that ultimately cannot succeed. The user gets a fast response, and no charge is ever lost or duplicated.
