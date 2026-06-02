# Authentication & Authorization

Every time you signed in to an app with "Continue with Google", or your session kept you logged in after a refresh, you were using the two ideas in this chapter. As a frontend engineer you've *consumed* auth — you stored a token, attached it to requests, redirected on a 401. Now you'll see what the backend does on the other side of the wire: deciding **who** a request is from, and **what** that person is allowed to do.

## Authentication vs Authorization (who you are vs what you may do)

These two words get mixed up constantly, but they answer different questions.

- **Authentication (authn)** = *Who are you?* Proving identity. Typing a password, completing the Google login, presenting a valid token — all authentication. The output is: "this request belongs to user #42."
- **Authorization (authz)** = *What are you allowed to do?* Deciding permissions. "User #42 is a regular member, so they can read posts but cannot delete other people's posts."

Analogy: authentication is showing your ID at the door of an office building. Authorization is whether your badge opens the server-room door. You can be fully authenticated (we know exactly who you are) and still be **un**authorized (you're not allowed in here). On the wire these map to two different HTTP statuses: **401 Unauthorized** means "we don't know who you are / your credentials are bad" (an authn failure), while **403 Forbidden** means "we know who you are, but you can't do this" (an authz failure).

Authentication always comes first: you can't decide what someone may do until you know who they are.

## Never store plaintext passwords (hashing + salt)

The single most important rule in this chapter: **never store a password as plaintext**, and never store it in a form you can reverse (like encryption with a key you hold). If your database leaks — and databases leak — every plaintext or reversible password is instantly compromised, and because people reuse passwords, you've also handed attackers their bank and email logins.

Instead you store a **hash**. A cryptographic hash function (like SHA-256) is a one-way blender: it turns `"hunter2"` into a fixed-length fingerprint, and there's no practical way to run it backwards to recover the input. When a user logs in, you hash what they typed and compare it to the stored hash. You never need the original password again.

But a plain hash isn't enough. Two users with the same password get the *same* hash, and attackers precompute giant lookup tables ("rainbow tables") mapping common passwords to their hashes. The fix is a **salt**: a random value mixed into each password before hashing. Now identical passwords produce different hashes, and the attacker's precomputed tables are worthless because they didn't include your salt.

You also want the hash to be **slow on purpose**. Fast hashes let attackers try billions of guesses per second. Purpose-built **password hashing** algorithms — **bcrypt**, **argon2**, and **PBKDF2** — are deliberately expensive (they iterate thousands of times), which barely affects one honest login but cripples brute-force attacks. In this chapter you'll use `hashlib.pbkdf2_hmac` with 100,000 iterations. In real production code, reach for bcrypt or argon2 via a library like `passlib` — and let it manage a unique random salt per user (we use a fixed salt only to make exercises reproducible).

## Sessions vs tokens (JWT) — and how a signed token works

Once a user is authenticated, the server must *remember* them across requests, because HTTP itself is stateless — each request arrives with no memory of the last. Two common strategies:

- **Server sessions.** On login the server creates a random session ID, stores the real user data server-side (in memory, Redis, or a DB), and sends the client only the opaque ID in a cookie. Every later request sends that cookie; the server looks it up. This is what classic "Continue with Google" flows often end with. Revoking is trivial — delete the session row and the user is logged out instantly.
- **Stateless tokens (JWT).** Instead of storing state on the server, you hand the client a **token that contains the facts** ("claims") — like `user:42, role:admin` — plus a **signature**. The server stores nothing; it trusts the token because it can verify the signature on each request.

How does the signature work? It's a **keyed fingerprint** of the payload using a secret only the server knows (an HMAC). You compute `signature = HMAC(secret, payload)` and send `payload.signature`. When the token comes back, you recompute the signature over the payload with your secret and check it matches. If anyone tampers with the payload (say, flips `role:member` to `role:admin`), the signature no longer matches and you reject it. Crucially, the signature proves *authenticity*, not secrecy — a JWT payload is readable by anyone, so **never put secrets in it**. The exercises here build a tiny "mini-JWT" exactly this way: `sign(payload, secret)` and `verify(token, secret)`.

The tradeoff: because a stateless token is trusted purely on its signature, you **can't easily revoke it before it expires**. With a server session you delete the row; with a JWT, until it expires the server will keep honoring it (unless you build extra machinery like a denylist, which gives back the statefulness you were trying to avoid). That's why JWTs carry short expiry times.

## Role-based access control (RBAC)

Authorization needs a model. The most common is **role-based access control**: each user has one or more **roles** (`member`, `editor`, `admin`), and a **policy** maps roles to allowed **actions**. Checking permission becomes a lookup: "does this user's role include the action they're attempting?" You'll implement this as `can(role, action, policy)` and `is_allowed(user_roles, required_roles)`.

Why roles instead of checking individual users? The same reason you use CSS classes instead of inline styles on every element: roles let you change the rule in one place. Grant "editors can delete drafts" once, and every editor gets it — no per-user edits.

## Common pitfalls (timing attacks, leaking secrets in responses)

- **Timing attacks.** When you compare a secret (a password hash, a token signature) with `==`, Python often stops at the first differing byte — so a wrong guess that shares a longer prefix takes measurably longer. An attacker can exploit those microsecond differences to recover the secret byte by byte. The fix is a **constant-time compare** that always examines every byte: `hmac.compare_digest`. You'll use it in `safe_equal` and in password/token verification.
- **Leaking secrets in responses.** It's shockingly easy to serialize a whole user object — including its `password` hash or active `token` — straight into a JSON response. Always **redact** sensitive fields before returning data (the `redact(user)` exercise), and return a *copy* so you never accidentally mutate your stored record. Treat password hashes, tokens, and secret keys as things that must never appear in any response, log line, or error message.

Keep these straight — authn before authz, hash-with-salt, sign-don't-trust, compare in constant time, redact on the way out — and you've got the backbone of safe auth.
