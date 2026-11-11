# Level 1: Easy (5 Problems)

| # | Title | Type | Topics |
|---|---|---|---|
| E1 | Team Welcome | Write the code | input, print, strings |
| E2 | Loud Name | Complete the code | string methods, concatenation |
| E3 | Broken Calculator | Fix the code | type conversion, arithmetic |
| E4 | Room Area | Write the code | input, type conversion, arithmetic |
| E5 | Even or Odd | Complete the code | %, if / else |

**Problem types:**
- **Write the code:** the student starts from an empty editor.
- **Complete the code:** the student gets code with blanks `____` and fills them.
- **Fix the code:** the student gets code with a mistake and fixes it.

---

## E1. Team Welcome
**Type:** Write the code · **Topics:** input, print, strings

### Problem
Read your team name, then print a welcome message.

### Input
One line: the team name.

### Output
Two lines:
```
Welcome, <team name>!
Good luck!
```

### Example
| Input | Output |
|---|---|
| `Tigers` | `Welcome, Tigers!`<br>`Good luck!` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `Tigers` | `Welcome, Tigers!` / `Good luck!` |
| `Team 5` | `Welcome, Team 5!` / `Good luck!` |
| `PSC` | `Welcome, PSC!` / `Good luck!` |

### Model Solution
```python
team = input()
print("Welcome, " + team + "!")
print("Good luck!")
```

---

## E2. Loud Name
**Type:** Complete the code · **Topics:** string methods, concatenation

### Problem
Read a name and say hello with the name in CAPITAL letters.
Fill the blanks `____` to make the code work.

### Given Code
```python
name = input()
name = name.____()
print("Hello, " + ____)
```

### Input
One line: a name.

### Output
`Hello, <NAME IN CAPITAL LETTERS>`

### Example
| Input | Output |
|---|---|
| `ahmed` | `Hello, AHMED` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `ahmed` | `Hello, AHMED` |
| `Mona` | `Hello, MONA` |
| `omar ali` | `Hello, OMAR ALI` |

### Model Solution
```python
name = input()
name = name.upper()
print("Hello, " + name)
```

---

## E3. Broken Calculator
**Type:** Fix the code · **Topics:** type conversion, arithmetic

### Problem
This program should read two numbers and print their sum.
But when the input is `3` and `5`, it prints `Sum: 35` instead of `Sum: 8`.
Find the mistake and fix it.

### Given Code
```python
a = input()
b = input()
print("Sum:", a + b)
```

### Input
Two lines: two whole numbers.

### Output
`Sum: <a + b>`

### Example
| Input | Output |
|---|---|
| `3`<br>`5` | `Sum: 8` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `3` / `5` | `Sum: 8` |
| `10` / `20` | `Sum: 30` |
| `-4` / `4` | `Sum: 0` |
| `100` / `250` | `Sum: 350` |

### The Bug
`input()` gives text, so `+` joins the texts. Fix: `int(input())`.

### Model Solution
```python
a = int(input())
b = int(input())
print("Sum:", a + b)
```

---

## E4. Room Area
**Type:** Write the code · **Topics:** input, type conversion, arithmetic

### Problem
You want to buy a carpet for your room. Read the length and the width of the room, then print the area.

**Area = length x width**

### Input
Two lines: length and width (whole numbers).

### Output
`Area: <area>`

### Example
| Input | Output |
|---|---|
| `5`<br>`3` | `Area: 15` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `5` / `3` | `Area: 15` |
| `10` / `10` | `Area: 100` |
| `7` / `1` | `Area: 7` |
| `12` / `4` | `Area: 48` |

### Model Solution
```python
length = int(input())
width = int(input())
print("Area:", length * width)
```

---

## E5. Even or Odd
**Type:** Complete the code · **Topics:** %, if / else

### Problem
Read a whole number. Print `Even` if it is even, or `Odd` if it is odd.
Fill the blanks `____` to make the code work.

### Given Code
```python
n = int(input())
if n ____ 2 == 0:
    print("Even")
____:
    print("Odd")
```

### Input
One line: a whole number.

### Output
`Even` or `Odd`

### Example
| Input | Output |
|---|---|
| `4` | `Even` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `4` | `Even` |
| `7` | `Odd` |
| `0` | `Even` |
| `-3` | `Odd` |

### Model Solution
```python
n = int(input())
if n % 2 == 0:
    print("Even")
else:
    print("Odd")
```
