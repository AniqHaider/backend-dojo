# Chapter 1: Python Fundamentals

## What is a program?

A **program** is a list of instructions a computer follows, one after another, to turn some *input* into some *output*. That's it. You already write programs every day in JavaScript — a React component takes props (input) and returns JSX (output). Python is just another language for writing those instructions, and it happens to be the most popular language for building **backends**.

A **backend** is the program that runs on a server (a computer in a data center, not in the user's browser). When your React app calls `fetch('/api/orders')`, some backend program receives that request, does work (looks things up, does math, saves data), and sends a response back. In this course, *you* are going to write those backend programs in Python.

The good news: the *thinking* you already do as a frontend engineer — managing state, transforming arrays, handling edge cases — is exactly the thinking backends need. You're learning new syntax, not a new brain.

## The Python runtime (vs the browser's JS engine)

When you write JavaScript, something has to actually *run* it. In the browser that's the **JS engine** (like V8 in Chrome). The engine reads your code and executes it.

Python has the same idea: the thing that runs your `.py` files is called the **Python interpreter** (or **runtime**). You install it on your machine or your server, then it reads your Python code top-to-bottom and executes each line.

A few differences that will trip up a JS person:

- **No `let`, `const`, or `var`.** In Python you just write `name = "Asha"`. The variable springs into existence on assignment.
- **Indentation is the syntax.** JS uses `{ }` to group code into blocks. Python uses **indentation** (spaces). The lines inside an `if` or a function must be indented the same amount. This is not optional styling — it's how Python knows what belongs together.
- **No semicolons needed.** One statement per line.
- **`#` starts a comment** (instead of `//`).

So this JS:
```js
function greet(name) {
  return "Hello, " + name;
}
```
becomes this Python:
```python
def greet(name):
    return "Hello, " + name
```

## Values and types

A **value** is a piece of data: the number `42`, the text `"hello"`, the truth value `True`. Every value has a **type** — a category that tells Python what the value *is* and what you can do with it.

The core Python types, with their JS cousins:

- **`int`** — a whole number, like `42`. (JS just has `number`.)
- **`float`** — a decimal number, like `3.14` or `2.0`.
- **`str`** — text ("string"), like `"Asha"`. Use single or double quotes.
- **`bool`** — `True` or `False` (capitalized! not `true`/`false`).
- **`None`** — "nothing here", like JS `null`/`undefined`.

Python is **strict about types**. In JS, `"3" + 4` gives `"34"` because JS silently converts. Python refuses: `"3" + 4` is an **error**. You must convert on purpose with `int("3")` or `str(4)`. This strictness feels annoying at first but it catches bugs — and bugs in a backend can corrupt a customer's order.

An **f-string** is Python's template literal. JS `` `Hello, ${name}!` `` becomes Python `f"Hello, {name}!"`. The `f` prefix turns on the `{ }` substitution.

## Collections: lists & dicts

Most backend work is shuffling **collections** of data around. Two types do almost all the work:

- A **`list`** is an ordered sequence — exactly like a JS array. `nums = [3, 1, 2]`. Index from zero: `nums[0]` is `3`. You can `nums.append(4)` (like `push`), slice it `nums[1:3]`, and loop over it.

- A **`dict`** ("dictionary") is a set of **key → value** pairs — like a JS object or a `Map`. `user = {"name": "Asha", "age": 30}`. Look up a value with `user["name"]`. Crucially, use `user.get("email", "n/a")` to read a key *that might not exist* and supply a fallback instead of crashing.

If you've used JSON, you already know these: JSON is literally just nested lists and dicts (arrays and objects). When data travels between your frontend and backend, it travels as JSON.

## Functions, conditionals, loops

A **function** is a reusable named block of instructions. Define it with `def`, give it **parameters**, and `return` a value:
```python
def total_price(qty, unit):
    return qty * unit
```

Important beginner trap: **`return` vs `print`**. `print(x)` displays text on the screen for a human to read. `return x` *hands the value back* to whatever called the function so the rest of the program can use it. A backend almost always needs to `return` data (to send it in a response), not `print` it. Returning `None` (the default when you forget to return) is a very common bug.

A **conditional** chooses between paths:
```python
if n % 2 == 0:
    result = "even"
else:
    result = "odd"
```
`%` is the **modulo** (remainder) operator — `10 % 3` is `1`. `==` tests equality.

A **loop** repeats work. `for x in nums:` walks through each item in a list. `range(5)` gives the numbers `0,1,2,3,4` — handy for counting.

Python also has **comprehensions**, a compact way to build a list from another:
```python
squares = [x * x for x in range(n)]
```
Think of it as `nums.map(...)` and `.filter(...)` fused into one expression.

When something might fail, wrap it in **`try` / `except`** so your program doesn't crash:
```python
try:
    value = 10 / divisor
except ZeroDivisionError:
    value = None
```
This is Python's `try/catch`.

## Why this matters for backends

Here's the punchline. A backend's whole life is: **receive data, transform it, send data back.** That incoming data — the body of a `POST /api/orders` request — arrives as exactly the structures in this chapter: **dicts and lists** (parsed from JSON).

So a request to create an order might arrive as:
```python
[{"name": "Mug", "qty": 2, "price": 50}, {"name": "Pen", "qty": 3, "price": 10}]
```
A list of dicts. Your job is to loop over it, read each dict's keys (carefully — what if `price` is missing?), do arithmetic (`qty * price`), accumulate a total, and `return` the result. That is precisely the mini-capstone at the end of this chapter.

Everything else you'll build — databases, APIs, authentication — sits on top of this. Master moving values through types, lists, dicts, and functions, and you've got the foundation of every backend you'll ever write.
