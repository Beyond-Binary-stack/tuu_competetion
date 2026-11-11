# ==========================================================
# LEVEL 1: EASY (5 Problems)
# ==========================================================


# ----------------------------------------------------------
# E1. Team Welcome
# Topics: input, print, strings
# Type: Write the code
# ----------------------------------------------------------
# Read your team name, then print a welcome message.
#
# Input:  One line: the team name.
# Output: Two lines:
#         Welcome, <team name>!
#         Good luck!
#
# Example:
#   Input:  Tigers
#   Output: Welcome, Tigers!
#           Good luck!
# ----------------------------------------------------------
team = input()
print("Welcome, " + team + "!")
print("Good luck!")


# ----------------------------------------------------------
# E2. Loud Name
# Topics: string methods, concatenation
# Type: Complete the code
# ----------------------------------------------------------
# Read a name and say hello with the name in CAPITAL letters.
# Fill the blanks ____ to make the code work.
#
# Given code:
#   name = input()
#   name = name.____()
#   print("Hello, " + ____)
#
# Input:  One line: a name.
# Output: Hello, <NAME IN CAPITAL LETTERS>
#
# Example:
#   Input:  ahmed
#   Output: Hello, AHMED
# ----------------------------------------------------------
name = input()
name = name.upper()
print("Hello, " + name)


# ----------------------------------------------------------
# E3. Broken Calculator
# Topics: type conversion, arithmetic
# Type: Fix the code
# ----------------------------------------------------------
# This program should read two numbers and print their sum.
# But when the input is 3 and 5, it prints "Sum: 35" instead of "Sum: 8".
# Find the mistake and fix it.
#
# Given code:
#   a = input()
#   b = input()
#   print("Sum:", a + b)
#
# Input:  Two lines: two whole numbers.
# Output: Sum: <a + b>
#
# Example:
#   Input:  3
#           5
#   Output: Sum: 8
#
# The bug: input() gives text, so + joins the texts. Use int(input()).
# ----------------------------------------------------------
a = int(input())
b = int(input())
print("Sum:", a + b)


# ----------------------------------------------------------
# E4. Room Area
# Topics: input, type conversion, arithmetic
# Type: Write the code
# ----------------------------------------------------------
# You want to buy a carpet for your room. Read the length and the width
# of the room, then print the area.
# Area = length x width
#
# Input:  Two lines: length and width (whole numbers).
# Output: Area: <area>
#
# Example:
#   Input:  5
#           3
#   Output: Area: 15
# ----------------------------------------------------------
length = int(input())
width = int(input())
print("Area:", length * width)


# ----------------------------------------------------------
# E5. Even or Odd
# Topics: %, if / else
# Type: Complete the code
# ----------------------------------------------------------
# Read a whole number. Print "Even" if it is even, or "Odd" if it is odd.
# Fill the blanks ____ to make the code work.
#
# Given code:
#   n = int(input())
#   if n ____ 2 == 0:
#       print("Even")
#   ____:
#       print("Odd")
#
# Input:  One line: a whole number.
# Output: Even or Odd
#
# Example:
#   Input:  4
#   Output: Even
# ----------------------------------------------------------
n = int(input())
if n % 2 == 0:
    print("Even")
else:
    print("Odd")
