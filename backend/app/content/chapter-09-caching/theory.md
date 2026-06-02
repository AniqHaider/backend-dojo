# Caching & Rate Limiting

As a frontend engineer you already cache things every day — the browser caches images, React memoizes components, a CDN serves your JS bundle from an edge node near the user. Backend caching is the same idea pointed at a different problem: **don't recompute or re-fetch something expensive when you already have the answer.** The twist is that on the backend, the "answer" is usually shared by thousands of users, so getting it slightly wrong (serving an old value) hurts everyone at once. That trade-off — speed vs. correctness — is the whole chapter.

## Why cache? (cost, load, latency)

Three reasons, and they reinforce each other.

**Latency.** Reading a value from memory takes microseconds. Reading the same value from a SQL query that joins three tables might take 50–200ms. If your homepage calls that query on every request, every user waits. Cache the result and the second request is effectively free.

**Load.** Every uncached request hits your database. Databases are the hardest thing to scale horizontally — you can add ten more web servers easily, but you usually have *one* primary database. If 10,000 requests per second all hit the DB, it falls over. A cache absorbs the repeated reads so the DB only sees the misses.

**Cost.** This connects to your EKS autoscaling story: when CPU and DB load climb, the autoscaler spins up more pods to keep latency acceptable — and you pay for every pod. A cache lets each pod answer more requests with less work, so you hit your latency targets with *fewer* pods. Caching is often the cheapest performance win you can buy: less compute, fewer instances, smaller bill.

## Where caches live (in-process vs. Redis)

**In-process (in-memory) cache.** A plain dictionary inside your application process. Fastest possible (no network hop), but it has two limits: it dies when the process restarts, and **each pod has its own copy.** With three pods you have three caches that don't agree with each other. Fine for small, rarely-changing data; dangerous when freshness matters.

**Shared cache (Redis / Memcached).** A separate server all your pods talk to over the network. Slightly slower than in-process (you pay a network round-trip), but every pod sees the *same* cached value, and it survives a pod restart. This is the default choice for backend caching at scale. Redis also gives you TTL expiry, atomic counters (great for rate limiting), and locks for free.

A common pattern is **both**: a tiny in-process cache in front of Redis to shave the network hop for the hottest keys.

## TTL and the cache-aside pattern

**TTL (time to live)** is how long a cached value is considered valid. You set it when you write the value: "keep this for 60 seconds." After that, the cache treats the entry as gone. TTL is your main safety valve — even if you never explicitly invalidate anything, a short TTL guarantees stale data self-corrects within that window.

The **cache-aside** (lazy-loading) pattern is the workhorse:

1. Request comes in. Look in the cache.
2. **Hit** → return the cached value. Done.
3. **Miss** → query the database, write the result into the cache with a TTL, then return it.

The application owns the cache logic; the cache itself is "aside" from the DB. Exercise 07 (`memoize_fib`) is cache-aside in miniature: check the dict, compute on miss, store the result.

## The hard part: invalidation & stale data

> "There are only two hard things in Computer Science: cache invalidation and naming things." — Phil Karlton

This is the answer to *"what problems does caching introduce?"* — and the one interviewers want to hear.

The moment you cache a value, you have created a **second copy of the truth.** The database is the source of truth; the cache is a snapshot of it. As soon as the source changes, your snapshot is **stale** — it's serving an old value that no longer matches reality. A user updates their profile name, but the cached page still shows the old name for 60 seconds because that's the TTL.

You have two ways to deal with staleness, and both have sharp edges:

- **TTL expiry (passive):** let entries expire on their own. Simple and self-healing, but you accept being wrong for up to one TTL. Choosing the TTL is a judgment call — too long means stale data, too short means you barely cache at all.
- **Explicit invalidation (active):** when the data changes, delete or overwrite the cache entry. Correct in theory, but *hard* in practice — you have to know **every** cache key that depends on the changed data and evict all of them, from every service that wrote one. Miss one and you serve stale data forever. This is why invalidation is famously hard: it's a distributed bookkeeping problem with no compiler to catch your mistakes.

The honest engineering answer: pick the **shortest TTL you can tolerate**, invalidate explicitly on writes where correctness really matters, and accept that some staleness is the price of the speed.

## Cache stampede & how to avoid it

A subtler problem. Imagine one very popular key with a 60-second TTL. At the exact second it expires, the next 5,000 concurrent requests all check the cache, all see a miss, and all run the expensive DB query *simultaneously* — because none of them has finished writing the value back yet. The DB gets hit 5,000 times for a value it should have computed once. That spike can take the database down. This is a **cache stampede** (also called a "thundering herd" or "dog-piling").

Three standard fixes:

- **Locking / single-flight:** the first request to miss acquires a lock and recomputes; everyone else waits for it and reuses the result. Only one DB query runs.
- **Early/probabilistic recompute:** refresh the value *before* it expires (e.g. a background job, or a random chance to recompute as expiry approaches), so it's never actually empty during a stampede.
- **Jitter:** never give many keys the *same* expiry time. Add a random offset (`ttl + random(0, 10s)`) so expirations spread out instead of all firing at once.

## Rate limiting (token bucket & fixed window)

Rate limiting is caching's cousin: instead of storing values, you store *counts* in fast storage (usually Redis) to decide whether to allow or reject a request. It protects you from abuse, runaway clients, and accidental traffic spikes.

**Fixed window** (exercise 06): count requests in a time window (e.g. "100 per minute"). Allow if the count is under the limit, otherwise reject. Dead simple. Its weakness: a client can fire 100 requests at 0:59 and another 100 at 1:01 — 200 requests in two seconds — because the window boundary resets the count.

**Token bucket** (exercise 05): imagine a bucket that holds up to `capacity` tokens and refills at a steady rate (e.g. 10 tokens/sec). Each request costs a token. If a token is available, allow and deduct it; if the bucket is empty, reject. This elegantly allows short **bursts** (spend the whole bucket at once) while enforcing a steady **average** rate over time. It's the most widely used algorithm because it matches how real traffic behaves: bursty, but bounded.

Both are deterministic given a clock — which is exactly why the exercises pass `now` in as an argument instead of calling the real clock. That keeps your logic testable, the same way you'd inject a mock timer in a frontend test.
