# ==========================================================
# LEVEL 2: MEDIUM (5 Problems)
# ==========================================================


# ----------------------------------------------------------
# M1. Pizza Party
# Topics: arithmetic (//, %)
# Type: Write the code
# ----------------------------------------------------------
# Friends share a pizza. Every person gets the same number of slices,
# and the rest stay in the box.
# Read the number of slices and the number of people, then print how many
# slices each person gets and how many are left.
# Hint: // gives the whole part of a division, % gives the remainder.
#
# Input:  Two lines: number of slices, number of people (whole numbers).
# Output: Each person: <slices per person>
#         Left: <slices left>
#
# Example:
#   Input:  10
#           3
#   Output: Each person: 3
#           Left: 1
#
# Hidden tests:
#   10 / 3 -> Each person: 3 / Left: 1
#   8  / 4 -> Each person: 2 / Left: 0
#   5  / 6 -> Each person: 0 / Left: 5
#   25 / 7 -> Each person: 3 / Left: 4
# ----------------------------------------------------------
slices = int(input())
people = int(input())
print("Each person:", slices // people)
print("Left:", slices % people)


# ----------------------------------------------------------
# M2. Phone Battery
# Topics: assignment operators, strings
# Type: Fix the code - 2 mistakes
# ----------------------------------------------------------
# This program reads the battery level, how much the phone was charged,
# and how much was used. Then it prints the new battery level.
# The code has 2 mistakes. Find them and fix them.
#
# Given code:
#   battery = int(input())
#   charge = int(input())
#   used = int(input())
#   battery =+ charge
#   battery -= used
#   print("Battery: " + battery + "%")
#
# Input:  Three lines: battery level, charge amount, used amount.
# Output: Battery: <level>%
#
# Example:
#   Input:  40
#           30
#           25
#   Output: Battery: 45%
#
# Hidden tests:
#   40 / 30 / 25 -> Battery: 45%
#   10 / 50 / 20 -> Battery: 40%
#   90 / 10 / 100 -> Battery: 0%
#   0  / 0  / 0   -> Battery: 0%
#
# The bugs:
#   1. =+ should be += (=+ just sets battery to the charge).
#   2. You cannot join text and a number with +. Use str(battery).
# ----------------------------------------------------------
battery = int(input())
charge = int(input())
used = int(input())
battery += charge
battery -= used
print("Battery: " + str(battery) + "%")


# ----------------------------------------------------------
# M3. Weather Advice
# Topics: if / elif / else, comparison
# Type: Complete the code
# ----------------------------------------------------------
# Read the temperature and give advice:
#   Less than 10  -> Cold
#   From 10 to 24 -> Nice
#   25 or more    -> Hot
# Fill the blanks ____ to make the code work.
# Given code:
#   temp = int(input())
#   if temp ____ 10:
#       print("Cold")
#   ____ temp < 25:
#       print("Nice")
#   ____:
#       print("Hot")
#
# Input:  One line: the temperature (whole number).
# Output: Cold, Nice, or Hot
#
# Example:
#   Input:  30
#   Output: Hot
#
# Hidden tests:
#   30  -> Hot
#   5   -> Cold
#   10  -> Nice
#   24  -> Nice
#   25  -> Hot
#   -3  -> Cold
# ----------------------------------------------------------
temp = int(input())
if temp < 10:
    print("Cold")
elif temp < 25:
    print("Nice")
else:
    print("Hot")


# ----------------------------------------------------------
# M4. Weekend Check
# Topics: string methods, logical or, if / else
# Type: Write the code
# ----------------------------------------------------------
# Read a day name. The day can have capital or small letters and extra spaces.
# If the day is friday or saturday, print "Weekend". Otherwise print "Work day".
# Hint: use .strip() and .lower() first.
#
# Input:  One line: a day name.
# Output: Weekend or Work day
#
# Example:
#   Input:  FRIDAY
#   Output: Weekend
#
# Hidden tests:
#   FRIDAY       -> Weekend
#   monday       -> Work day
#   "  Saturday " -> Weekend
#   Sunday       -> Work day
# ----------------------------------------------------------
day = input().strip().lower()
if day == "friday" or day == "saturday":
    print("Weekend")
else:
    print("Work day")


# ----------------------------------------------------------
# M5. Rocket Countdown
# Topics: while loop, assignment operators
# Type: Fix the code
# ----------------------------------------------------------
# This program should count down from a number to 1, then print "Go!".
# But it never stops! Find the mistake and fix it.
#
# Given code:
#   n = int(input())
#   while n > 0:
#       print(n)
#   print("Go!")
#
# Input:  One line: a whole number (0 or more).
# Output: The numbers from n down to 1 (one per line), then Go!
#
# Example:
#   Input:  3
#   Output: 3
#           2
#           1
#           Go!
#
# Hidden tests:
#   3 -> 3 / 2 / 1 / Go!
#   1 -> 1 / Go!
#   0 -> Go!
#   5 -> 5 / 4 / 3 / 2 / 1 / Go!
#
# The bug: n never changes, so n > 0 is always True. Add n -= 1.
# ----------------------------------------------------------
n = int(input())
while n > 0:
    print(n)
    n -= 1
print("Go!")
