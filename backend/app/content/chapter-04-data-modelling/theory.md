# Data Modelling, Indexes & Transactions

You already know how to read and combine data with SQL. This chapter is about the decisions you make *before* the queries: how to shape your tables, how to make reads fast, and how to make writes safe. Think of it as the difference between knowing JavaScript syntax and knowing how to architect a frontend app — same language, much bigger thinking.

## From spreadsheets to a real schema

Most people's first mental model of a database is a giant spreadsheet: one big sheet with every column you might ever need. That works for ten rows. It falls apart fast.

Imagine a bookings spreadsheet where every row repeats the user's name, email, the movie title, and its rating. If Asha changes her email, you now have to find and edit *every* row she appears in. Miss one, and your data disagrees with itself — some rows say `asha@old.com`, others `asha@new.com`. Which one is true?

A **schema** is the deliberate design of your tables: what tables exist, what columns each has, what types those columns are, and how the tables relate. The core idea is *each fact lives in exactly one place*. A user's email lives once, in the `users` table. A booking just **points** at that user.

This is very close to how you already think in frontend code. You don't copy a `user` object into every component that needs it — you keep one source of truth (a store, context, a prop passed down) and reference it. A relational schema is the same instinct, enforced by the database.

## Primary & foreign keys recap

A **primary key** is the column that uniquely identifies each row in a table — usually `id`. No two rows share it, and it's never null. It's the row's permanent address.

A **foreign key** is a column in one table that stores the primary key of a row in another table. In our seed, `bookings.user_id` is a foreign key pointing at `users.id`. That single number says "this booking belongs to that user" without copying the user's data.

In JS terms: instead of embedding the whole object (`booking.user = {...}`), you store a reference (`booking.userId = 1`) and look it up when needed — which is exactly what a `JOIN` does.

Foreign keys aren't just documentation. When you declare one, the database **enforces** it: it will refuse to insert a booking for `user_id = 99` if no user 99 exists, and (depending on config) refuse to delete a user who still has bookings. This guarantee is called **referential integrity** — your references can never dangle.

## Indexes: the book's index analogy (fast reads, costed writes)

Suppose you have a million users and run `SELECT * FROM users WHERE email = 'asha@x.com'`. Without help, the database checks every single row — a **sequential scan** (or "seq scan"). A million comparisons to find one row.

An **index** fixes this. Picture a textbook: to find "transactions" you don't read all 400 pages, you flip to the index at the back, find the word, and jump to the page. A database index is the same — a separate, sorted lookup structure that maps a column's values to the rows that hold them. With an index on `email`, the database jumps straight to the match.

It feels free, but it isn't. The index is extra data the database must **keep in sync**. Every `INSERT`, `UPDATE`, or `DELETE` now has to update the table *and* every index on it. So indexes make reads faster but writes slower, and they cost disk space. The lesson: index the columns you frequently filter, join, or sort on — not every column "just in case."

## Transactions & ACID (all-or-nothing)

Booking a seat is really two steps: mark the seat taken, and create the booking row. What if the server crashes between them? The seat is locked but no booking exists — a ghost reservation no one can fix.

A **transaction** groups multiple statements so they succeed or fail as one unit:

```sql
BEGIN;
  UPDATE seats SET status = 'booked' WHERE id = 3;
  INSERT INTO bookings (user_id, seat_id) VALUES (1, 3);
COMMIT;
```

If anything fails before `COMMIT`, you `ROLLBACK` and it's as if nothing happened. This is the **atomicity** of **ACID**:

- **A**tomicity — all steps apply, or none do.
- **C**onsistency — the database moves from one valid state to another; rules like foreign keys and unique constraints always hold.
- **I**solation — concurrent transactions don't see each other's half-finished work.
- **D**urability — once committed, the data survives a crash.

If you've used a database transaction in a payment flow, this is why: you never want money moved but the order not recorded. Frontend analogy: it's like an optimistic UI update you `rollback` if the request fails — except the database guarantees it for real, on disk.

## Reading a query plan with EXPLAIN ANALYZE

When a query is slow, you don't guess — you ask the database what it's doing. Prefix any query with `EXPLAIN ANALYZE`:

```sql
EXPLAIN ANALYZE SELECT * FROM users WHERE email = 'asha@x.com';
```

This runs the query and prints the **query plan**: the steps the database chose, its row estimates, and the *real* time each step took. The thing to hunt for is a **Seq Scan** on a big table where you expected an index — that's your sign a useful index is missing. After adding one, the plan should switch to an **Index Scan** and the timing should drop. It's the database equivalent of opening browser DevTools' performance panel instead of guessing why a page is janky.

## Normalization vs denormalization

**Normalization** is the discipline of splitting data so each fact lives once (the schema design we started with). It minimizes duplication and makes updates safe — change the email in one place, done. The cost is that answering a question may require joining several tables.

**Denormalization** is the deliberate opposite: copying or pre-computing data to avoid joins and make reads faster. A `bookings` table might cache `movie_title` so a dashboard doesn't join three tables on every page load. The cost is the duplication problem we opened with — now you must keep the copies in sync.

There's no universally "correct" choice; it's a tradeoff. Start normalized — it's safer and simpler to reason about. Denormalize later, intentionally, only when a real read-performance problem demands it. It mirrors a frontend call you already make: normalized state (a single store) versus caching derived data in a component for speed, accepting that you now own keeping it fresh.
