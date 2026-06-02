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
- **Optimistic vs pessimistic locking** — pessimistic = lock the row up front (`SELECT ... FOR UPDATE`); optimistic = don't lock, but check a *version*/timestamp at write time and retry if it changed.
- **ACID** — Atomicity, Consistency, Isolation, Durability: the guarantees a transaction gives you. "Wrap it in a transaction" is shorthand for all four.
- **Eventual consistency** — replicas/caches may briefly disagree but converge; the opposite of *strong consistency*.
- **Rate limiting** — capping requests per client (token bucket / leaky bucket) to protect the service.
- **Circuit breaker** — after repeated downstream failures, stop calling it for a cooldown so you fail fast instead of piling up.
- **Exponential backoff** — space out retries (1s, 2s, 4s…) with *jitter* so retries don't synchronize into a thundering herd.
- **Indexing** — a B-tree lookup structure that turns a full *table scan* into a seek; the first fix for a slow `WHERE`/`JOIN`.
- **Connection pooling** — reuse a fixed set of DB connections; *pool exhaustion* is a classic peak-traffic failure.
- **N+1 query** — one query for the list plus one per row; fix with a join or eager load.
- **Read replicas** — copies of the DB that serve reads to offload the primary; watch *replication lag*.
- **Sharding / partitioning** — split one big dataset across nodes by a *shard key* when it no longer fits or one node can't keep up.
- **Cache invalidation** — keeping cached data from going *stale*; "the hardest problem in computing" for good reason.

## Scaling basics (vertical vs horizontal, replicas, sharding, load balancing)

- **Vertical scaling (scale up)** — give one machine more CPU/RAM. Simple, no code changes, but you hit a ceiling and it's a single point of failure.
- **Horizontal scaling (scale out)** — add more machines behind a **load balancer** that spreads traffic. Requires your app to be *stateless* (session state lives in a cache/DB, not in memory).
- **Read replicas** — for *read-heavy* workloads, route reads to replicas and writes to the primary. Cheap and effective; just account for replication lag (a read right after a write may see old data).
- **Caching** — put a cache (e.g. Redis) in front of the DB to absorb hot reads; this often buys more headroom than any DB change.
- **Sharding** — the last resort, when the *write* volume or *dataset size* exceeds a single node. Pick a shard key carefully (avoid hot shards). Cross-shard queries get painful, so you shard only when you must.

The interview ordering is: **cache → read replicas → scale out the app → shard the data.** Reach for the cheap, low-risk options first.

## Reliability patterns recap

When you call something that can fail — a payment provider, an email API, another service — assume it *will*:

- **Timeouts** — never wait forever; a hung call holds a connection and a thread.
- **Retries with exponential backoff + jitter** — retry transient failures, but back off so you don't hammer a struggling dependency.
- **Circuit breaker** — trip open after N failures, fail fast during the cooldown, then half-open to test recovery.
- **Idempotency** — retries are only safe if the operation is idempotent, so design for it (idempotency keys, unique constraints).
- **Queues / background jobs** — offload slow or flaky work so the request returns fast; the job retries on its own and smooths out load spikes.
- **Graceful degradation** — return a cached or partial response rather than a 500 when a non-critical dependency is down.

## Be concise & structured (what interviewers reward)

The single biggest scoring lever at the junior level is *not* knowing more — it's communicating cleanly. Concretely:

- **Lead with the named concept**, then explain. "I'd use an idempotency key. Here's why…" beats five sentences that circle the idea without naming it.
- **Think out loud, but stay structured** — narrate Problem → Risks → Solution → Edge cases instead of free-associating.
- **State your assumptions** ("assuming a single relational DB and moderate traffic") so the interviewer can correct scope instead of failing you on it.
- **Admit the tradeoff.** Every real answer has one — "this adds latency but guarantees correctness." Acknowledging it shows engineering judgment.
- **Don't over-engineer.** Suggesting Kafka and sharding for a 100-user app is a red flag. Match the solution to the scale; reach for the simplest thing that works.
- **Recover gracefully when stuck.** "I'm not sure of the exact term, but the idea is to check a version before writing and retry if it changed" still earns most of the credit — that's optimistic locking, and you described it correctly.

These are the exact ten questions you were asked before. This time you have the names. Drill them until the model answer is reflex.
