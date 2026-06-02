# Building an API with FastAPI

## What an API actually is (you've been calling them from the frontend)

Every time you wrote `fetch("/api/products")` on the frontend, *something* on a
server received that request, did some work, and sent back JSON. That
"something" is an **API** — an Application Programming Interface. It's just a
contract: "if you send me an HTTP request shaped like *this*, I'll send you a
response shaped like *that*."

You already know the client half cold. You've set methods (`GET`, `POST`), added
headers, attached JSON bodies, and read `response.status` and
`response.json()`. Backend work is simply writing the **other end** of that same
conversation. Nothing magical happens on the server — it reads the incoming
request, runs ordinary functions, and returns ordinary data. This chapter teaches
the *logic* inside those functions, because that logic is plain Python you can
test without a running server.

## Request → handler → response

An HTTP request arrives with a few key parts:

- **Method** — the verb: `GET` (read), `POST` (create), `PUT`/`PATCH` (update),
  `DELETE` (remove).
- **Path** — the URL after the domain, e.g. `/users/42`.
- **Query string** — the bit after `?`, e.g. `?page=2&size=10`.
- **Body** — JSON you send with `POST`/`PUT` (the same object you'd put in
  `fetch`'s `body`).

The server matches the method + path to a **handler** — a function you wrote.
The handler does its job (look something up, validate input, save a row) and
**returns a response**: a status code plus a body. Think of it as:

```
incoming request  ->  your_function(request)  ->  { status, body }
```

That's the entire mental model. A FastAPI route is just a Python function with a
decorator on top. The framework parses the request for you and serializes your
return value to JSON — the work you write is the function body.

## Status codes that matter (2xx / 4xx / 5xx)

The status code is a 3-digit number that tells the client *how it went*, before
they even read the body. You've seen these in the Network tab. The first digit
is the category:

- **2xx — success.** `200 OK` (here's your data), `201 Created` (I made the
  thing you asked for), `204 No Content` (done, nothing to send back — common for
  `DELETE`).
- **4xx — *you* (the client) messed up.** `400 Bad Request` (malformed input),
  `401 Unauthorized` (not logged in), `403 Forbidden` (logged in but not
  allowed), `404 Not Found` (no such resource), `422 Unprocessable Entity`
  (validation failed — FastAPI's default for bad bodies).
- **5xx — *the server* messed up.** `500 Internal Server Error` (your code
  threw). 5xx is never the client's fault — it's a bug or outage on your side.

Picking the right code is part of designing a good API. A frontend dev consuming
your API relies on these: they branch on `if (res.status === 404)` instead of
parsing error strings.

## Path vs query params, request bodies

Two ways to pass values in the URL, and they mean different things:

- **Path parameters** identify *which* resource. In `/users/42`, the `42` is a
  path param — it's part of the resource's address. Use it for required,
  identifying values.
- **Query parameters** come after `?` and *modify* the request: filtering,
  sorting, pagination. In `/products?page=2&size=10`, `page` and `size` are
  query params. They're typically optional and have defaults.

Rule of thumb: if removing the value makes the URL point at a *different thing*,
it's a path param. If it just changes *how* you see the same collection, it's a
query param.

The **request body** carries the actual payload for creates and updates — the
new user's name and email, say. It's the server-side counterpart to the object
you `JSON.stringify` into `fetch`'s `body`. Bodies belong on `POST`/`PUT`/`PATCH`,
not `GET`.

## FastAPI: routes, Pydantic models, automatic docs

**FastAPI** is a Python web framework. Three pieces you'll use constantly:

1. **Routes** — decorate a function to bind it to a method + path:

   ```python
   @app.get("/users/{user_id}")
   def get_user(user_id: int):
       return {"id": user_id, "name": "Ada"}
   ```

   `{user_id}` is a path param; FastAPI reads it, converts it to `int`, and
   passes it in. Query params and bodies arrive as function arguments too.

2. **Pydantic models** — classes that declare the *shape* of your data, like a
   TypeScript `interface` that actually runs. FastAPI uses them to validate
   incoming bodies automatically; if a required field is missing or the type is
   wrong, the client gets a `422` *before your code runs* — you never have to
   hand-write that check.

   ```python
   from pydantic import BaseModel
   class NewUser(BaseModel):
       name: str
       email: str
   ```

3. **Automatic docs** — because your types are declared, FastAPI generates
   interactive API documentation at `/docs` for free. No Swagger config, no
   Postman collection to maintain by hand.

You return a plain `dict` (or a Pydantic model) and FastAPI turns it into a JSON
response with `200` by default. Override the code with the
`status_code=` argument or by raising `HTTPException(404, ...)`.

## Shaping responses & never leaking secrets

Your database row is **not** your API response. A `user` row might contain a
`password` hash, an internal `is_admin` flag, or audit columns. Returning the row
verbatim leaks those to the client. Always **shape** the response: build the
public object explicitly and copy over only the fields the client should see.

Two habits to internalize:

- **Whitelist, don't blacklist.** Prefer building a new dict with the allowed
  keys over deleting the forbidden ones — when someone adds a new secret column
  later, a whitelist stays safe by default.
- **Don't mutate the input.** If you remove a key, copy the dict first
  (`{**user}`), so the original data the rest of your code holds isn't altered.

These response-shaping functions are pure logic — give them a dict, get a dict
back — which is exactly what the exercises in this chapter drill. Master the
handler logic here, and wiring it into FastAPI routes is the easy part.
