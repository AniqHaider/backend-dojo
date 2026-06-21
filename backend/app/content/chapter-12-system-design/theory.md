# System Design & Interview Drills

This is the payoff chapter. Everything you learned about Python, SQL, APIs, auth, concurrency, caching, and resilience now gets compressed into the format that actually decides interviews: short, high-pressure questions where you have to name the right concept and reason out loud. Below is your cheat-sheet — read it the morning of the interview.

## How to answer system-design questions (Problem → Risks → Solution → Edge cases)

Junior backend interviews rarely want a full distributed-systems essay. They want to see that you think in a structured way and reach for the *named* tool. Use this four-beat answer to almost any "how would you handle X" question:

1. **Problem** — restate what could go wrong in one sentence. ("Two requests could hit the same row at the same time and both think they won.")
2. **Risks** — name the failure mode precisely: *race condition*, *stale data*, *duplicate write*, *cascading failure*. Naming the risk proves you understand it.
3. **Solution** — reach for the standard pattern by its real name: *idempotency key*, *SELECT ... FOR UPDATE*, *exponential backoff*, *read replica*. Interviewers grade on vocabulary as much as logic.
4. **Edge cases** — show maturity: "What if the retry arrives after the first one committed? The idempotency key still returns the original result." This is the part that separates a hire from a maybe.

Say these beats out loud. Even if your solution isn't perfect, the structure signals you've done this before.

## The vocabulary that signals seniority

These are the words that make an interviewer relax. Use them correctly and unprompted.

- **Idempotency** — an operation you can safely repeat and get the same result; the client sends an *idempotency key* so retries don't double-charge.

[[exercise:ch12-ex01-idempotency-duplicate-payment]]

- **Optimistic vs pessimistic locking** — pessimistic = lock the row up front (`SELECT ... FOR UPDATE`); optimistic = don't lock, but check a *version*/timestamp at write time and retry if it changed.

[[exercise:ch12-ex04-row-locking-double-book]]
- **ACID** — Atomicity, Consistency, Isolation, Durability: the guarantees a transaction gives you. "Wrap it in a transaction" is shorthand for all four.
- **Eventual consistency** — replicas/caches may briefly disagree but converge; the opposite of *strong consistency*.
- **Rate limiting** — capping requests per client (token bucket / leaky bucket) to protect the service.
- **Circuit breaker** — after repeated downstream failures, stop calling it for a cooldown so you fail fast instead of piling up.
- **Exponential backoff** — space out retries (1s, 2s, 4s…) with *jitter* so retries don't synchronize into a thundering herd.
- **Indexing** — a B-tree lookup structure that turns a full *table scan* into a seek; the first fix for a slow `WHERE`/`JOIN`. Before you add one, run `EXPLAIN ANALYZE` on the query: it shows the planner's actual execution plan, so you can confirm a *sequential scan* is the culprit and verify the index removes it — diagnose with `EXPLAIN` before you reach for any fix.

[[exercise:ch12-ex02-explain-analyze-slow-query]]

- **Connection pooling** — reuse a fixed set of DB connections; *pool exhaustion* is a classic peak-traffic failure. When a service is fast off-peak but slow only under load, suspect a resource that's fine when idle but saturates under concurrency — the pool runs out and requests queue waiting for a free connection.

[[exercise:ch12-ex10-debug-slow-at-peak]]
- **N+1 query** — one query for the list plus one per row; fix with a join or eager load.
- **Read replicas** — copies of the DB that serve reads to offload the primary; watch *replication lag*.
- **Sharding / partitioning** — split one big dataset across nodes by a *shard key* when it no longer fits or one node can't keep up.
- **Cache invalidation** — keeping cached data from going *stale*; "the hardest problem in computing" for good reason. A cache buys you speed by absorbing hot reads, but the price is exactly this: once the underlying data changes, the cached copy can be wrong until you invalidate it.

[[exercise:ch12-ex03-caching-invalidation-tradeoff]]

## Scaling basics (vertical vs horizontal, replicas, sharding, load balancing)

- **Vertical scaling (scale up)** — give one machine more CPU/RAM. Simple, no code changes, but you hit a ceiling and it's a single point of failure.
- **Horizontal scaling (scale out)** — add more machines behind a **load balancer** that spreads traffic. Requires your app to be *stateless* (session state lives in a cache/DB, not in memory).
- **Read replicas** — for *read-heavy* workloads, route reads to replicas and writes to the primary. Cheap and effective; just account for replication lag (a read right after a write may see old data).

[[exercise:ch12-ex11-scaling-reads-replicas]]

- **Caching** — put a cache (e.g. Redis) in front of the DB to absorb hot reads; this often buys more headroom than any DB change.
- **Sharding** — the last resort, when the *write* volume or *dataset size* exceeds a single node. Pick a shard key carefully (avoid hot shards). Cross-shard queries get painful, so you shard only when you must.

The interview ordering is: **cache → read replicas → scale out the app → shard the data.** Reach for the cheap, low-risk options first. The headline distinction to keep straight: *scaling up* (vertical) means a bigger box, *scaling out* (horizontal) means more boxes behind a load balancer, and *sharding* is the last resort you reach for only when writes or dataset size outgrow a single node.

[[exercise:ch12-ex12-scale-up-vs-out-shard]]

## Reliability patterns recap

When you call something that can fail — a payment provider, an email API, another service — assume it *will*:

- **Timeouts** — never wait forever; a hung call holds a connection and a thread.
- **Retries with exponential backoff + jitter** — retry transient failures, but back off so you don't hammer a struggling dependency.
- **Circuit breaker** — trip open after N failures, fail fast during the cooldown, then half-open to test recovery.
- **Idempotency** — retries are only safe if the operation is idempotent, so design for it (idempotency keys, unique constraints).
- **Queues / background jobs** — offload slow or flaky work so the request returns fast; the job retries on its own and smooths out load spikes.
- **Graceful degradation** — return a cached or partial response rather than a 500 when a non-critical dependency is down.

When the failing dependency is *someone else's* service — a payment provider, an email API — you combine these: short timeouts so a hung call can't block you, retries with backoff for transient blips, and a circuit breaker so repeated failures make you fail fast instead of piling up.

[[exercise:ch12-ex07-resilience-third-party]]

Background jobs deserve their own callout. When a request triggers several slow or external steps — send a welcome email, generate a PDF, call an analytics API — doing them inline makes the user wait and couples your response to every dependency's reliability. Push that work onto a *message queue* and a worker processes it after the request returns: the user gets a fast response, and each step retries independently if it fails.

[[exercise:ch12-ex08-background-jobs-queues]]

## Security & data-modeling fundamentals (the ones they slip in)

A few non-scaling questions show up constantly at the junior level — answer them crisply and you bank easy points.

**Authentication vs authorization.** These get confused, so nail the one-liner: *authentication* is verifying **who you are** (logging in, checking a password or token); *authorization* is deciding **what you're allowed to do** once you're known (can this user delete that order?). Authn comes first, then authz.

[[exercise:ch12-ex05-authn-vs-authz]]

**Never trust the client.** Frontend validation is for UX — instant feedback — not security. A malicious user can bypass your React form entirely and call the API directly with curl, so the backend must re-validate every input. The rule is simple: *client validation is a convenience, server validation is the guarantee.*

[[exercise:ch12-ex06-server-side-validation]]

**Normalization vs denormalization.** *Normalized* data splits things into related tables joined by foreign keys: no duplication, so updates are safe and consistent, but reads pay the cost of joins. *Denormalized* data duplicates fields into one wide table: reads are fast with no joins, but every copy must be kept in sync on writes. The tradeoff is **write-safety/consistency vs read-speed** — normalize by default, denormalize only when read performance demands it.

[[exercise:ch12-ex09-normalize-vs-denormalize]]

## Be concise & structured (what interviewers reward)

The single biggest scoring lever at the junior level is *not* knowing more — it's communicating cleanly. Concretely:

- **Lead with the named concept**, then explain. "I'd use an idempotency key. Here's why…" beats five sentences that circle the idea without naming it.
- **Think out loud, but stay structured** — narrate Problem → Risks → Solution → Edge cases instead of free-associating.
- **State your assumptions** ("assuming a single relational DB and moderate traffic") so the interviewer can correct scope instead of failing you on it.
- **Admit the tradeoff.** Every real answer has one — "this adds latency but guarantees correctness." Acknowledging it shows engineering judgment.
- **Don't over-engineer.** Suggesting Kafka and sharding for a 100-user app is a red flag. Match the solution to the scale; reach for the simplest thing that works.
- **Recover gracefully when stuck.** "I'm not sure of the exact term, but the idea is to check a version before writing and retry if it changed" still earns most of the credit — that's optimistic locking, and you described it correctly.

These are the exact ten questions you were asked before. This time you have the names. Drill them until the model answer is reflex.
