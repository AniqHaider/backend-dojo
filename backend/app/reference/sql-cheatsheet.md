# SQL syntax cheatsheet

A quick reference for the SQL you'll write against the TicketPay database (tables like `users`, `movies`, `showtimes`, `seats`, `bookings`). Each entry shows the **shape** — swap in your own tables and columns.

## SELECT basics

```sql
SELECT col_a, col_b FROM table;     -- pick columns
SELECT * FROM movies;               -- every column
SELECT title AS name FROM movies;   -- rename a column in the output
```

## WHERE (filtering rows)

```sql
SELECT * FROM bookings
WHERE status = 'confirmed';

WHERE price > 100
WHERE genre IN ('drama', 'comedy')
WHERE title LIKE 'The %'      -- % is the wildcard
WHERE deleted_at IS NULL      -- use IS NULL, never = NULL
WHERE a AND b      WHERE a OR b      WHERE NOT a
```

## ORDER BY & LIMIT

```sql
SELECT * FROM movies
ORDER BY rating DESC      -- DESC = high→low, ASC = low→high (default)
LIMIT 5;                  -- only the first 5 rows

ORDER BY rating DESC, title ASC   -- tie-break on a second column
```

## Aggregates & GROUP BY

```sql
COUNT(*)        SUM(price)        AVG(rating)
MIN(price)      MAX(price)

SELECT movie_id, COUNT(*) AS bookings
FROM bookings
GROUP BY movie_id;            -- one row per movie_id

SELECT movie_id, COUNT(*) AS n
FROM bookings
GROUP BY movie_id
HAVING COUNT(*) > 3;          -- filter GROUPS (WHERE filters rows)
```

Rule of thumb: every non-aggregated column in `SELECT` must appear in `GROUP BY`.

## JOINs (combining tables)

```sql
SELECT b.id, m.title
FROM bookings AS b
JOIN movies AS m ON m.id = b.movie_id;     -- only matching rows

LEFT JOIN movies AS m ON m.id = b.movie_id; -- keep all left rows; NULLs if no match
```

Pattern: join on the **foreign key** (`b.movie_id`) equalling the other table's **primary key** (`m.id`). Use short table aliases (`b`, `m`) to keep it readable.

## DISTINCT (unique rows)

```sql
SELECT DISTINCT genre FROM movies;   -- drop duplicate genres
```

## INSERT / UPDATE / DELETE

```sql
INSERT INTO seats (showtime_id, label, status)
VALUES (1, 'A1', 'free');

UPDATE seats SET status = 'booked'
WHERE id = 42;               -- ALWAYS include a WHERE, or every row changes

DELETE FROM bookings
WHERE status = 'cancelled';
```

## Transactions

```sql
BEGIN;
  UPDATE seats SET status = 'booked' WHERE id = 42;
  INSERT INTO bookings (seat_id, user_id) VALUES (42, 7);
COMMIT;     -- all-or-nothing; ROLLBACK; undoes everything since BEGIN
```

## Locking (concurrency)

```sql
SELECT * FROM seats
WHERE id = 42
FOR UPDATE;   -- lock these rows so another transaction must wait
```

## Indexes

```sql
CREATE INDEX idx_bookings_movie ON bookings (movie_id);
-- speeds up WHERE / JOIN on movie_id; costs a little on every write
```

## Handy functions

```sql
COALESCE(value, fallback)    -- first non-NULL value
NOW()                        -- current timestamp
COUNT(DISTINCT user_id)      -- unique count
CAST(price AS int)           -- change a value's type
```
