# Level 2: Medium (5 Problems)

| # | Title | Type | Topics |
|---|---|---|---|
| M1 | Pizza Party | Write the code | arithmetic (`//`, `%`) |
| M2 | Phone Battery | Fix the code | assignment operators, strings |
| M3 | Weather Advice | Complete the code | if / elif / else, comparison |
| M4 | Weekend Check | Write the code | string methods, logical `or`, if / else |
| M5 | Rocket Countdown | Fix the code | while loop, assignment operators |

---

## M1. Pizza Party
**Type:** Write the code · **Topics:** arithmetic (`//`, `%`)

### Problem
Friends share a pizza. Every person gets the same number of slices, and the rest stay in the box.
Read the number of slices and the number of people, then print how many slices each person gets and how many are left.

**Hint:** `//` gives the whole part of a division, `%` gives the remainder.

### Input
Two lines: number of slices, number of people (whole numbers).

### Output
```
Each person: <slices per person>
Left: <slices left>
```

### Example
| Input | Output |
|---|---|
| `10`<br>`3` | `Each person: 3`<br>`Left: 1` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `10` / `3` | `Each person: 3` / `Left: 1` |
| `8` / `4` | `Each person: 2` / `Left: 0` |
| `5` / `6` | `Each person: 0` / `Left: 5` |
| `25` / `7` | `Each person: 3` / `Left: 4` |

### Model Solution
```python
slices = int(input())
people = int(input())
print("Each person:", slices // people)
print("Left:", slices % people)
```

---

## M2. Phone Battery
**Type:** Fix the code · **Topics:** assignment operators, strings

### Problem
This program reads the battery level, how much the phone was charged, and how much was used. Then it prints the new battery level.
The code has **2 mistakes**. Find them and fix them.

### Given Code
```python
battery = int(input())
charge = int(input())
used = int(input())
battery =+ charge
battery -= used
print("Battery: " + battery + "%")
```

### Input
Three lines: battery level, charge amount, used amount (whole numbers).

### Output
`Battery: <level>%`

### Example
| Input | Output |
|---|---|
| `40`<br>`30`<br>`25` | `Battery: 45%` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `40` / `30` / `25` | `Battery: 45%` |
| `10` / `50` / `20` | `Battery: 40%` |
| `90` / `10` / `100` | `Battery: 0%` |
| `0` / `0` / `0` | `Battery: 0%` |

### The Bugs
1. `=+` should be `+=` (`=+` just sets battery to the charge).
2. You cannot join text and a number with `+`. Use `str(battery)` or an f-string.

### Model Solution
```python
battery = int(input())
charge = int(input())
used = int(input())
battery += charge
battery -= used
print("Battery: " + str(battery) + "%")
```

---

## M3. Weather Advice
**Type:** Complete the code · **Topics:** if / elif / else, comparison

### Problem
Read the temperature and give advice:
- Less than 10: `Cold`
- From 10 to 24: `Nice`
- 25 or more: `Hot`

Fill the blanks `____` to make the code work.

### Given Code
```python
temp = int(input())
if temp ____ 10:
    print("Cold")
____ temp < 25:
    print("Nice")
____:
    print("Hot")
```

### Input
One line: the temperature (whole number).

### Output
`Cold`, `Nice`, or `Hot`

### Example
| Input | Output |
|---|---|
| `30` | `Hot` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `30` | `Hot` |
| `5` | `Cold` |
| `10` | `Nice` |
| `24` | `Nice` |
| `25` | `Hot` |
| `-3` | `Cold` |

### Model Solution
```python
temp = int(input())
if temp < 10:
    print("Cold")
elif temp < 25:
    print("Nice")
else:
    print("Hot")
```

---

## M4. Weekend Check
**Type:** Write the code · **Topics:** string methods, logical `or`, if / else

### Problem
Read a day name. The day can have capital or small letters and extra spaces.
If the day is `friday` or `saturday`, print `Weekend`. Otherwise print `Work day`.

**Hint:** use `.strip()` and `.lower()` first.

### Input
One line: a day name.

### Output
`Weekend` or `Work day`

### Example
| Input | Output |
|---|---|
| `FRIDAY` | `Weekend` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `FRIDAY` | `Weekend` |
| `monday` | `Work day` |
| `  Saturday ` | `Weekend` |
| `Sunday` | `Work day` |

### Model Solution
```python
day = input().strip().lower()
if day == "friday" or day == "saturday":
    print("Weekend")
else:
    print("Work day")
```

---

## M5. Rocket Countdown
**Type:** Fix the code · **Topics:** while loop, assignment operators

### Problem
This program should count down from a number to 1, then print `Go!`.
But it never stops! (Time Limit Exceeded). Find the mistake and fix it.

### Given Code
```python
n = int(input())
while n > 0:
    print(n)
print("Go!")
```

### Input
One line: a whole number (0 or more).

### Output
The numbers from n down to 1 (one per line), then `Go!`

### Example
| Input | Output |
|---|---|
| `3` | `3`<br>`2`<br>`1`<br>`Go!` |

### Hidden Test Cases
| Input | Expected Output |
|---|---|
| `3` | `3` / `2` / `1` / `Go!` |
| `1` | `1` / `Go!` |
| `0` | `Go!` |
| `5` | `5` / `4` / `3` / `2` / `1` / `Go!` |

### The Bug
`n` never changes, so `n > 0` is always True. Add `n -= 1` inside the loop.

### Model Solution
```python
n = int(input())
while n > 0:
    print(n)
    n -= 1
print("Go!")
```
