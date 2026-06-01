# SQL Fundamentals (PostgreSQL)

Welcome. You already know how to build interfaces. This chapter is about the place all that data on screen actually *lives*: the **database**. We'll use PostgreSQL (often just "Postgres"), one of the most popular open-source databases, and the language you talk to it with: **SQL**.

We'll use a running example: a movie-ticket app called **TicketPay** — it has movies, showtimes, seats, users, and bookings. Same kind of app you might build a frontend for.

## What is a database? (why not just files or variables?)

A **database** is a program whose entire job is to store data safely and let you fetch it back quickly and correctly.

As a frontend dev, you've held data in JavaScript variables and in React state. That works while the page is open — but the moment the user refreshes or closes the tab, it's gone. Variables live in memory, and memory is temporary.

"Okay," you might say, "so write it to a file." You *could* save a big JSON file. But problems pile up fast:

- **Concurrency:** what happens when two users book the same seat at the same instant? With a raw file, both might read "seat free", both write "booked" — and you've double-sold it. Databases handle this with **transactions** so only one wins.
- **Searching:** finding "all bookings by Asha" in a 2-million-line JSON file means reading the whole thing. A database uses **indexes** (like a book's index) to jump straight to the answer.
- **Integrity:** a database can *refuse* bad data — e.g. a booking pointing at a user that doesn't exist.

So a database is like the difference between scribbling orders on loose napkins (files) versus a well-run restaurant ledger that never loses an order, never lets two waiters claim the same table, and can instantly tell you today's totals.

## Tables, rows, columns (like a spreadsheet, but strict)

Data in a relational database lives in **tables**. A table is a lot like a spreadsheet tab:

- A **column** is a named field with a fixed type — e.g. `title` is text, `rating` is a number. Every value in that column must match the type.
- A **row** (also called a *record*) is one entry — one movie, one user, one booking.

Here's TicketPay's `movies` table:

| id | title      | rating |
|----|------------|--------|
| 1  | Dune       | 8.5    |
| 2  | Inside Out | 8.1    |
| 3  | Tenet      | 7.4    |

The "strict" part is the key difference from a spreadsheet: you can't accidentally put the word "soon" in the `rating` column. The database enforces the **schema** — the agreed shape of each table. This strictness is a feature: your code can trust that `rating` is always a number.

## Primary keys & foreign keys (how tables link)

Notice the `id` column above. That's a **primary key** — a column whose value uniquely identifies each row. No two movies share an `id`. It's the row's permanent name tag.

Now look at `bookings`:

| id | user_id | showtime_id | seat_id |
|----|---------|-------------|---------|
| 1  | 1       | 1           | 1       |

`user_id` here is a **foreign key**: it stores the primary key of a row in *another* table (`users`). So booking 1 belongs to user 1 (Asha). This is how relational databases avoid copying data everywhere — instead of repeating "Asha, asha@example.com" inside every booking, you store her once in `users` and just *point* to her by id.

If you've used React, think of it like keeping data normalized: store each entity once, reference it by id. Same instinct.

## SQL: asking questions of your data (SELECT/WHERE/ORDER BY)

**SQL** (Structured Query Language) is how you talk to the database. The most common command is `SELECT`, which *reads* data. SQL reads almost like English:

```sql
SELECT title FROM movies WHERE rating > 8.0;
```

That says: "give me the `title` column, from the `movies` table, but only rows where `rating` is above 8.0." The clauses:

- `SELECT` — which columns you want (`*` means all columns).
- `FROM` — which table.
- `WHERE` — a filter; only rows matching the condition come back.
- `ORDER BY column DESC` — sort results (DESC = high to low, ASC = low to high).
- `LIMIT n` — return at most `n` rows (great for "top 5").

A query always returns a **result set** — itself a little table of rows and columns. You can rename an output column with `AS`, e.g. `SELECT COUNT(*) AS total`.

## Changing data (INSERT/UPDATE/DELETE)

Reading is only half the job. Three commands change data:

- `INSERT INTO users (id, name, email) VALUES (4, 'Dev', 'dev@example.com');` — add a new row.
- `UPDATE movies SET rating = 8.0 WHERE id = 3;` — change existing rows that match the `WHERE`.
- `DELETE FROM seats WHERE id = 9;` — remove rows that match the `WHERE`.

A giant warning that every backend engineer learns once (painfully): **`UPDATE` and `DELETE` without a `WHERE` clause hit every row in the table.** `DELETE FROM seats;` empties the whole table. Always include a `WHERE`.

In Postgres you can add `RETURNING` to see what changed, e.g. `UPDATE movies SET rating = 8.0 WHERE id = 3 RETURNING title, rating;` hands back the rows it touched. Handy for confirming — and we use it in the exercises so your work is checkable.

## Combining tables (JOINs) & summarizing (GROUP BY)

Because data is split across tables (movies here, bookings there), you often need to stitch them back together. That's a **JOIN**.

```sql
SELECT b.id AS booking_id, u.name
FROM bookings b
JOIN users u ON b.user_id = u.id;
```

This matches each booking to its user by lining up `b.user_id` with `u.id`. (`b` and `u` are short *aliases* for the table names.) This is an **INNER JOIN**: it only keeps rows that have a match on both sides.

A **LEFT JOIN** keeps *every* row from the left table even if there's no match on the right — the missing side comes back as `NULL` (SQL's "no value"). Use it for questions like "every movie *and* how many showtimes it has, including movies with zero."

To **summarize**, use aggregate functions with `GROUP BY`:

- `COUNT(*)` — how many rows.
- `AVG(col)`, `SUM(col)`, `MIN`, `MAX` — math over a column.

`GROUP BY user_id` collapses rows into one group per user, so `COUNT(*)` becomes "bookings per user." To filter *groups* (not rows), use `HAVING` instead of `WHERE` — e.g. "only users with more than 1 booking."

## Why backends rely on this

Almost every backend you'll build is, at its core, a thin layer that translates HTTP requests into SQL and shapes the results into JSON for a frontend like the ones you've built. "Load the user's bookings" is a `SELECT` with a `JOIN`. "Cancel a booking" is a `DELETE`. "Book a seat" is an `INSERT` wrapped in a transaction so two users can't grab the same seat.

The database is also your source of truth and your safety net: it enforces types, prevents orphaned references via foreign keys, and keeps data consistent even under heavy concurrent traffic. Master these few commands and you've got the foundation for the vast majority of backend data work. Let's practice.
