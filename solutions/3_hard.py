# ==========================================================
# LEVEL 3: HARD (5 Problems)
# ==========================================================


# ----------------------------------------------------------
# H1. Leap Year  (Write the code)
# Topics: %, logical and / or, if / else
# ----------------------------------------------------------
# Read a year and check if it is a leap year.
# A year is a leap year if:
#   - it can be divided by 4 AND cannot be divided by 100,
#   - OR it can be divided by 400.
# Hint: a number x can be divided by 4 when x % 4 == 0.
#
# Input:  One line: a year.
# Output: Leap year or Not a leap year
#
# Example:
#   Input:  2024
#   Output: Leap year
# ----------------------------------------------------------
year = int(input())
if (year % 4 == 0 and year % 100 != 0) or year % 400 == 0:
    print("Leap year")
else:
    print("Not a leap year")


# ----------------------------------------------------------
# H2. Guess the Number  (Complete the code)
# Topics: while True, break, assignment, if / elif
# ----------------------------------------------------------
# The secret number is 7. The player keeps guessing until they find it.
# For each guess print "Too low", "Too high", or "Correct! Tries: N" and then stop.
# Fill the blanks ____ to make the code work.
#
# Given code:
#   tries = 0
#   while ____:
#       guess = int(input())
#       tries ____ 1
#       if guess < 7:
#           print("Too low")
#       elif guess > 7:
#           print("Too high")
#       else:
#           print("Correct! Tries:", tries)
#           ____
#
# Input:  Many lines, each one is a guess. The number 7 always appears.
# Output: One line for each guess.
#
# Example:
#   Input:  3
#           9
#           7
#   Output: Too low
#           Too high
#           Correct! Tries: 3
# ----------------------------------------------------------
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


# ----------------------------------------------------------
# H3. Admin Login  (Fix the code - 2 mistakes)
# Topics: nested if, comparison, indentation
# ----------------------------------------------------------
# This program checks a username and a password:
#   - Username admin and password 1234 -> Welcome admin
#   - Username admin and wrong password -> Wrong password
#   - Any other username               -> Unknown user
# The code has 2 mistakes. Find them and fix them.
#
# Given code:
#   username = input()
#   password = input()
#   if username == "admin":
#       if password = "1234":
#           print("Welcome admin")
#       else:
#       print("Wrong password")
#   else:
#       print("Unknown user")
#
# Input:  Two lines: username, password.
# Output: Welcome admin, Wrong password, or Unknown user
#
# Example:
#   Input:  admin
#           1234
#   Output: Welcome admin
#
# The bugs:
#   1. = should be == in the comparison (SyntaxError).
#   2. print("Wrong password") must be indented under else: (IndentationError).
# ----------------------------------------------------------
username = input()
password = input()
if username == "admin":
    if password == "1234":
        print("Welcome admin")
    else:
        print("Wrong password")
else:
    print("Unknown user")


# ----------------------------------------------------------
# H4. Digit Counter  (Write the code)
# Topics: while loop, //, %, assignment
# ----------------------------------------------------------
# Read a positive whole number. Print how many digits it has and the sum
# of its digits. Do it with a while loop (not with len() or strings).
# Hint: n % 10 gives the last digit, n // 10 removes the last digit.
#
# Input:  One line: a positive whole number.
# Output: Digits: <count>
#         Sum: <sum of digits>
#
# Example:
#   Input:  4096
#   Output: Digits: 4
#           Sum: 19
# ----------------------------------------------------------
n = int(input())
count = 0
total = 0
while n > 0:
    total += n % 10
    n //= 10
    count += 1
print("Digits:", count)
print("Sum:", total)


# ----------------------------------------------------------
# H5. Shop Discount  (Write the code)
# Topics: float, if / elif, nested if, f-strings
# ----------------------------------------------------------
# A shop gives a discount based on the price:
#   - Price 500 or more -> 20% discount
#   - Price 200 or more -> 10% discount
#   - Less than 200     -> no discount
# Members get an extra 5% discount (only when the answer is yes).
# Read the price and the member answer, then print the final price
# with 2 decimals.
# Example: price 600, member yes -> 20% + 5% = 25% -> 600 - 150 = 450.00
# Hint: print(f"Final price: {final:.2f}")
#
# Input:  Two lines: price (number), member (yes or no).
# Output: Final price: <price with 2 decimals>
#
# Example:
#   Input:  600
#           yes
#   Output: Final price: 450.00
# ----------------------------------------------------------
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
