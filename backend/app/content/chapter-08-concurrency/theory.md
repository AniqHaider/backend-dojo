# Concurrency, Locking & Idempotency

This is the chapter that separates "it works on my machine" from "it works when 10,000 people hit it at once." As a frontend dev, you usually deal with **one** user at a time — your code runs in their browser, for them. A backend is different: it serves **many users simultaneously**, and they constantly step on each other. Get this wrong and you double-sell a concert seat or charge a customer's card twice. Get it right and your API stays correct under pressure.

We'll keep using **TicketPay** (movies, showtimes, seats, bookings) and two real-world disasters: **two people booking the last seat**, and **a payment that gets charged twice**.

## Why concurrency is hard (two requests at once)

"Concurrency" just means *more than one thing happening at the same time*. Your backend doesn't handle requests one-at-a-time in a tidy line — it handles many **at once**, across different processes, servers, and database connections.

The trap is that operations you *think* of as a single step are actually several steps. Booking a seat feels like one action, but the server really does:

1. **Read**: is seat A3 free?
2. **Decide**: yes, it's free.
3. **Write**: mark A3 as booked for this user.

Between step 1 and step 3, *time passes*. If a second request sneaks in during that gap, it also reads "free" before anyone has written "booked." Now both think they won. In a single-user frontend this never happens. On a busy backend, it happens constantly. The whole chapter is about closing that gap.

## Race conditions (the last-seat problem)

A **race condition** is a bug where the result depends on the *timing* of operations that overlap — whoever "wins the race" changes the outcome, and usually nobody planned for two racers.

The last-seat problem, step by step:

- Seat A3 is the only one left.
- Asha's request reads: A3 free.
- Ben's request reads: A3 free. *(both read before either wrote)*
- Asha's request writes: A3 booked by Asha.
- Ben's request writes: A3 booked by Ben — **overwriting Asha**.

Two customers, two confirmation emails, one seat. The root cause is **not** a typo or a slow server — it's that the read and the write weren't protected as one indivisible unit. The fix is to make "check it's free AND book it" happen together, so a second racer can't slip in between.

[[exercise:ch8-ex09-quiz-last-seat-race]]

When several requests do race for the same resource and you have a record of each attempt, a clean tie-breaking rule is **first writer wins**: whoever arrived earliest (the smallest timestamp) gets it, and if two tie on time you fall back to the smallest id. It's a deterministic way to pick a single winner after the fact.

[[exercise:ch8-ex08-first-writer-wins]]

## Transactions & atomic conditional updates

A **transaction** groups several database statements so they either *all* happen or *none* do — and while it runs, the database keeps other transactions from corrupting it. This is the database doing the hard concurrency work for you.

The simplest, most powerful tool is the **atomic conditional update**: fold the check and the change into one statement.

```sql
UPDATE seats
SET booked_by = 2
WHERE id = 3 AND booked_by IS NULL
RETURNING id;
```

The `WHERE ... AND booked_by IS NULL` says "only book it *if it's still free*." The database guarantees this runs as one indivisible step, so two requests can't both pass the check. The loser's `UPDATE` simply matches **0 rows**.

[[exercise:ch8-ex01-atomic-guarded-update]]

That "0 rows affected" is the heartbeat of safe backends. **One row changed = you won. Zero rows changed = someone beat you to it** — show the user "seat just taken," don't error out. You'll practice both the winning update and the no-op update in the exercises.

[[exercise:ch8-ex02-update-noop-someone-won]]

Sometimes claiming a resource is an **insert**, not an update — you add a fresh `bookings` row for the seat. Use `INSERT ... RETURNING` to get back exactly what you just claimed, and in a real system you'd add a uniqueness rule (e.g. on `seat_id`) so a second insert for the same seat fails instead of double-booking.

[[exercise:ch8-ex03-claim-seat-insert]]

## Optimistic vs pessimistic locking

Sometimes one statement isn't enough — you need to read data, do some work, then write. Two strategies:

**Pessimistic locking** assumes conflicts are *likely*, so you lock the row up front:

```sql
SELECT id, label FROM seats WHERE id = 3 FOR UPDATE;
```

`SELECT ... FOR UPDATE` locks the selected rows. Any other transaction that tries to touch them **waits in line** until you commit. Safe and simple, but it makes others wait — so it's best when contention is genuinely high (the last seat to a sold-out show).

[[exercise:ch8-ex04-select-for-update]]

[[exercise:ch8-ex12-quiz-select-for-update]]

**Optimistic locking** assumes conflicts are *rare*, so you don't lock — you just *check at the end* that nothing changed underneath you, usually with a `version` number:

1. Read the row and its `version` (say, 5).
2. Do your work.
3. `UPDATE ... SET value = ?, version = 6 WHERE id = ? AND version = 5`.

If someone else wrote first, `version` is no longer 5, your update hits **0 rows**, and you retry. No waiting, no locks held — cheap and fast **when collisions are uncommon**. That's the sweet spot for optimistic locking: low contention, a quick version check, no one blocked.

[[exercise:ch8-ex06-optimistic-lock]]

Rule of thumb: **low contention → optimistic; high contention → pessimistic.**

[[exercise:ch8-ex10-quiz-optimistic-vs-pessimistic]]

## Idempotency keys (the duplicate-payment fix)

Now the one that bit you in the interview. A user taps "Pay." The network is flaky, so their phone never sees the response and **retries** — sending the *same* payment request twice. Without protection, you charge the card twice. The retry wasn't a new intent; it was the same intent, sent again.

The fix is an **idempotency key**. *Idempotent* means "doing it again has no extra effect." The client generates a unique key per payment intent (e.g. a UUID) and sends it with every attempt, including retries:

1. Request arrives with key `pay_abc123`.
2. Backend checks: have I seen `pay_abc123` before?
3. **No** → charge the card, store the result *under that key*.
4. **Yes** → skip charging; return the **stored** result from the first time.

So the first request charges; every retry returns the original outcome **without a second charge**. The client can retry as much as it likes, safely. You'll implement exactly this `process_payments` logic in the exercises — first-time keys charge, repeated keys return the same result with `charged: false`.

[[exercise:ch8-ex05-idempotency]]

This is why payment APIs (Stripe and friends) require an idempotency key on charge requests. It's not optional polish — it's the difference between a happy customer and a chargeback.

[[exercise:ch8-ex11-quiz-double-submit-payment]]

The same idea shows up for any event stream with **at-least-once delivery**: a message broker may hand you the *same* event more than once. The cure is the same shape — track the ids you've already processed and drop later duplicates, keeping only the **first occurrence** (in order). That's deduping by id.

[[exercise:ch8-ex07-dedupe-by-id]]

## Reservation / hold patterns with expiry

There's a gentler middle ground for things like seats and inventory: a **hold** (reservation). Instead of locking for the whole checkout, you place a temporary claim:

- User picks A3 → mark it **held by Asha until 10:05** (a 5-minute timer).
- A held seat isn't bookable by others, so nobody else can grab it while Asha pays.
- Asha pays in time → the hold becomes a confirmed booking.
- Asha abandons checkout → the hold **expires** and the seat quietly returns to the pool.

The expiry is the key idea: a crashed or distracted user can't lock a seat *forever*. A background job (or a `WHERE expires_at < now()` check) reclaims stale holds. This pattern gives users a fair window to finish without holding a database lock the entire time — you get safety *and* a good UX.

---

**The big picture:** concurrency bugs come from a read and a write that weren't protected as one unit. Your toolkit — atomic conditional updates, locks, idempotency keys, and timed holds — all exist to close that gap. Master these and "two users, one seat" and "charged twice" stop being scary interview questions and become routine.
