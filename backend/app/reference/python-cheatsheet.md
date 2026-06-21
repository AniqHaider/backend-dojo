# Python syntax cheatsheet

A quick reference for the syntax you'll reach for most. Each entry shows the **shape** of the code — fill in your own names and logic. Coming from JavaScript? The JS equivalent is noted where it helps.

## Variables & comments

```python
name = "Asha"        # no let/const/var — just assign
count = 0
PRICE = 50           # CONSTANTS are written in caps by convention
# this is a comment   (JS: //)
```

Indentation **is** the syntax. The lines inside an `if`, loop, or function must be indented (4 spaces). JS uses `{ }`; Python uses indentation.

## Types & conversion

```python
42        # int   (whole number)
3.14      # float (decimal)
"hello"   # str   (text — single or double quotes)
True      # bool  (capital T/F — not true/false)
None      # "nothing"  (JS: null/undefined)
```

Python does **not** auto-convert. Convert on purpose:

```python
int("42")     # "42" -> 42
str(42)       # 42 -> "42"
float("2.5")  # "2.5" -> 2.5
```

## Strings

```python
f"Hello, {name}!"    # f-string — like JS `Hello, ${name}!`
"a,b,c".split(",")   # -> ["a", "b", "c"]
"a b".split()        # split on spaces -> ["a", "b"]
"".join(["a","b"])   # -> "ab"   (glue a list of strings)
text.upper()         # -> uppercase
text.lower()         # -> lowercase
word[0]              # first character
word[-1]             # last character
text[1:4]            # slice: chars 1,2,3
```

## Numbers & math

```python
a + b    a - b    a * b
a / b    # division — ALWAYS a float (6 / 3 -> 2.0)
a // b   # integer division (7 // 2 -> 3)
a % b    # modulo / remainder (10 % 3 -> 1)
a ** b   # power (2 ** 3 -> 8)
total += n   # add n to total (shorthand for total = total + n)
```

## Lists

```python
nums = [3, 1, 2]
nums[0]            # first item -> 3
nums[-1]           # last item -> 2
nums.append(4)     # add to end (JS: push)
len(nums)          # how many items
nums[1:3]          # slice
sorted(nums)       # NEW sorted list -> [1, 2, 3]
sum(nums)          # add them up
```

## Sets (unique values)

```python
set([1, 1, 2])     # -> {1, 2}   duplicates removed (unordered)
sorted(set(nums))  # unique values, back in order, as a list
```

## Dicts (key → value)

```python
user = {"name": "Asha", "age": 30}
user["name"]              # -> "Asha"  (crashes if key missing)
user.get("email", "n/a")  # safe read with a fallback
user["email"] = "a@b.c"   # add / update a key
user.items()              # (key, value) pairs to loop over
```

## Conditionals

```python
if n % 2 == 0:
    result = "even"
elif n == 1:
    result = "one"
else:
    result = "odd"
```

```python
a and b      # both true   (JS: &&)
a or b       # either true  (JS: ||)
not a        # negate      (JS: !)
==  !=  <  >  <=  >=        # comparisons
```

## Loops

```python
for x in items:        # loop each item in a list
    print(x)

for i in range(5):     # 0, 1, 2, 3, 4
    print(i)

for k, v in d.items(): # loop a dict's key/value pairs
    print(k, v)

total = 0
for n in nums:         # the "running total" pattern
    total += n
```

## Comprehensions (compact list building)

```python
[x * x for x in range(n)]          # like nums.map(...)
[x for x in nums if x % 2 == 0]    # map + filter fused
```

## Functions

```python
def add(a, b):         # define; a, b are parameters
    return a + b       # hand a value back (NOT print)

def greet(name, greeting="Hi"):   # default parameter value
    return f"{greeting}, {name}"

def make_url(base, **params):     # collect extra keyword args into a dict
    # calling make_url("/x", a=1, b=2) -> params == {"a": 1, "b": 2}
    ...
```

**`return` vs `print`:** `print(x)` shows text on screen. `return x` hands the value back so the rest of the program (and the test harness) can use it. Forgetting `return` makes a function quietly return `None` — a very common bug.

## Errors (try / except)

```python
try:
    value = 10 / divisor
except ZeroDivisionError:
    value = None         # handle the specific failure
```

This is Python's `try/catch`. Catch the **specific** error type when you can.
