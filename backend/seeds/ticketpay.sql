-- TicketPay practice dataset (the capstone's domain).
-- Loaded into a disposable per-exercise schema by the SQL runner, so these
-- statements are intentionally unqualified (no schema prefix) and rely on the
-- runner having set the search_path.

CREATE TABLE users (
    id    INTEGER PRIMARY KEY,
    name  TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE movies (
    id     INTEGER PRIMARY KEY,
    title  TEXT NOT NULL,
    rating NUMERIC(3,1) NOT NULL
);

CREATE TABLE showtimes (
    id        INTEGER PRIMARY KEY,
    movie_id  INTEGER NOT NULL REFERENCES movies(id),
    starts_at TIMESTAMP NOT NULL,
    screen    TEXT NOT NULL
);

CREATE TABLE seats (
    id          INTEGER PRIMARY KEY,
    showtime_id INTEGER NOT NULL REFERENCES showtimes(id),
    label       TEXT NOT NULL
);

CREATE TABLE bookings (
    id          INTEGER PRIMARY KEY,
    user_id     INTEGER NOT NULL REFERENCES users(id),
    showtime_id INTEGER NOT NULL REFERENCES showtimes(id),
    seat_id     INTEGER NOT NULL REFERENCES seats(id),
    created_at  TIMESTAMP NOT NULL
);

INSERT INTO users (id, name, email) VALUES
    (1, 'Asha',   'asha@example.com'),
    (2, 'Ben',    'ben@example.com'),
    (3, 'Chitra', 'chitra@example.com');

INSERT INTO movies (id, title, rating) VALUES
    (1, 'Dune',       8.5),
    (2, 'Inside Out', 8.1),
    (3, 'Tenet',      7.4);

INSERT INTO showtimes (id, movie_id, starts_at, screen) VALUES
    (1, 1, '2026-06-10 18:00:00', 'A'),
    (2, 2, '2026-06-10 20:30:00', 'B'),
    (3, 1, '2026-06-11 18:00:00', 'C');

INSERT INTO seats (id, showtime_id, label) VALUES
    (1, 1, 'A1'), (2, 1, 'A2'), (3, 1, 'A3'), (4, 1, 'A4'),
    (5, 2, 'B1'), (6, 2, 'B2'),
    (7, 3, 'C1'), (8, 3, 'C2'), (9, 3, 'C3');

INSERT INTO bookings (id, user_id, showtime_id, seat_id, created_at) VALUES
    (1, 1, 1, 1, '2026-06-01 09:00:00'),
    (2, 2, 1, 2, '2026-06-01 09:05:00'),
    (3, 1, 2, 5, '2026-06-01 10:00:00'),
    (4, 3, 3, 7, '2026-06-02 11:00:00');
