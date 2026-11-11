# Level 3: Hard (5 Problems)

| # | Title | Type | Topics |
|---|---|---|---|
| H1 | Leap Year | Write the code | `%`, logical `and` / `or`, if / else |
| H2 | Guess the Number | Complete the code | while True, break, assignment, if / elif |
| H3 | Admin Login | Fix the code | nested if, comparison, indentation |
| H4 | Digit Counter | Write the code | while loop, `//`, `%`, assignment |
| H5 | Shop Discount | Write the code | float, if / elif, nested if, f-strings |

---

## H1. Leap Year
**Type:** Write the code · **Topics:** `%`, logical `and` / `or`, if / else

### Problem
Read a year and check if it is a leap year.

A year is a leap year if:
- it can be divided by 4 **and** cannot be divided by 100,
- **or** it can be divided by 400.

**Hint:** a number `x` can be divided by 4 when `x % 4 == 0`.

### Input
One line: a year.

### Output
`Leap year` or `Not a leap year`

### Example
| Input | Output |
|---|---|
| `2024` | `Leap year` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `2024` | `Leap year` |
| `2023` | `Not a leap year` |
| `1900` | `Not a leap year` |
| `2000` | `Leap year` |
| `2100` | `Not a leap year` |
| `1600` | `Leap year` |

### Model Solution
```python
year = int(input())
if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
    print("Leap year")
else:
    print("Not a leap year")
```

---

## H2. Guess the Number
**Type:** Complete the code · **Topics:** while True, break, assignment, if / elif

### Problem
The secret number is **7**. The player keeps guessing until they find it.
For each guess print `Too low`, `Too high`, or `Correct! Tries: N` and then stop.
Fill the blanks `____` to make the code work.

### Given Code
```python
tries = 0
while ____:
    guess = int(input())
    tries ____ 1
    if guess < 7:
        print("Too low")
    elif guess > 7:
        print("Too high")
    else:
        print("Correct! Tries:", tries)
        ____
```

### Input
Many lines, each one is a guess. The number 7 always appears. Ignore anything after it.

### Output
One line for each guess.

### Example
| Input | Output |
|---|---|
| `3`<br>`9`<br>`7` | `Too low`<br>`Too high`<br>`Correct! Tries: 3` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `3` / `9` / `7` | `Too low` / `Too high` / `Correct! Tries: 3` |
| `7` | `Correct! Tries: 1` |
| `1` / `2` / `3` / `4` / `5` / `6` / `7` | `Too low` x6 / `Correct! Tries: 7` |
| `10` / `8` / `7` / `100` | `Too high` / `Too high` / `Correct! Tries: 3` |
| `-5` / `50` / `7` | `Too low` / `Too high` / `Correct! Tries: 3` |

### Model Solution
```python
tries = 0
while True:
    guess = int(input())
    tries += 1
    if guess < 7:
        print("Too low")
    elif guess > 7:
        print("Too high")
    else:
        print("Correct! Tries:", tries)
        break
```

---

## H3. Admin Login
**Type:** Fix the code · **Topics:** nested if, comparison, indentation

### Problem
This program checks a username and a password:
- Username `admin` and password `1234`: print `Welcome admin`
- Username `admin` and wrong password: print `Wrong password`
- Any other username: print `Unknown user`

The code has **2 mistakes**. Find them and fix them.

### Given Code
```python
username = input()
password = input()
if username == "admin":
    if password = "1234":
        print("Welcome admin")
    else:
    print("Wrong password")
else:
    print("Unknown user")
```

### Input
Two lines: username, password.

### Output
`Welcome admin`, `Wrong password`, or `Unknown user`

### Example
| Input | Output |
|---|---|
| `admin`<br>`1234` | `Welcome admin` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `admin` / `1234` | `Welcome admin` |
| `admin` / `0000` | `Wrong password` |
| `ali` / `1234` | `Unknown user` |
| `Admin` / `1234` | `Unknown user` |

### The Bugs
1. `=` should be `==` in the comparison (SyntaxError).
2. `print("Wrong password")` must be indented under `else:` (IndentationError).

### Model Solution
```python
username = input()
password = input()
if username == "admin":
    if password == "1234":
        print("Welcome admin")
    else:
        print("Wrong password")
else:
    print("Unknown user")
```

---

## H4. Digit Counter
**Type:** Write the code · **Topics:** while loop, `//`, `%`, assignment

### Problem
Read a positive whole number. Print how many digits it has and the sum of its digits.
Do it with a `while` loop (not with `len()` or strings).

**Hint:** `n % 10` gives the last digit, `n // 10` removes the last digit.

### Input
One line: a positive whole number.

### Output
```
Digits: <count>
Sum: <sum of digits>
```

### Example
| Input | Output |
|---|---|
| `4096` | `Digits: 4`<br>`Sum: 19` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `4096` | `Digits: 4` / `Sum: 19` |
| `7` | `Digits: 1` / `Sum: 7` |
| `1000` | `Digits: 4` / `Sum: 1` |
| `99999` | `Digits: 5` / `Sum: 45` |

### Model Solution
```python
n = int(input())
count = 0
total = 0
while n > 0:
    total += n % 10
    n //= 10
    count += 1
print("Digits:", count)
print("Sum:", total)
```

---

## H5. Shop Discount
**Type:** Write the code · **Topics:** float, if / elif, nested if, f-strings

### Problem
A shop gives a discount based on the price:
- Price 500 or more: **20%** discount
- Price 200 or more: **10%** discount
- Less than 200: no discount

Members get an **extra 5%** discount (only when the answer is `yes`).
Read the price and the member answer, then print the final price with 2 decimals.

**Example:** price 600, member yes: discount = 20% + 5% = 25%, final = 600 - 150 = 450.00

**Hint:** `print(f"Final price: {final:.2f}")`

### Input
Two lines: price (number), member (`yes` or `no`).

### Output
`Final price: <price with 2 decimals>`

### Example
| Input | Output |
|---|---|
| `600`<br>`yes` | `Final price: 450.00` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `600` / `yes` | `Final price: 450.00` |
| `600` / `no` | `Final price: 480.00` |
| `300` / `yes` | `Final price: 255.00` |
| `200` / `no` | `Final price: 180.00` |
| `100` / `no` | `Final price: 100.00` |
| `100` / `yes` | `Final price: 95.00` |
| `500` / `no` | `Final price: 400.00` |

### Model Solution
```python
price = float(input())
member = input()
if price >= 500:
    discount = 20
elif price >= 200:
    discount = 10
else:
    discount = 0
if member == "yes":
    discount += 5
final = price - price * discount / 100
print(f"Final price: {final:.2f}")
```
