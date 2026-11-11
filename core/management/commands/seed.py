"""Seed the contest: problems, test cases, 5 groups, admin user, contest row."""
import os
import secrets

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from core.models import Contest, Group, Problem, TestCase
from core import runner


def expected_output(code, stdin_text):
    r = runner.run_code(code, stdin_text)
    if r["status"] != "ok" or r["err"]:
        raise RuntimeError(f"solution failed for input {stdin_text!r}: {r['err'][:300]}")
    return r["out"]


# Each problem: slug, title, level, lesson, statement_html,
# (seq/order are computed from the position in this list; keep it sorted easy -> medium -> hard)
# input_format, output_format, hint, starter_code, tests[list of stdin], solution
PROBLEMS = [
    # ================= EASY (10) =================
    dict(
        slug="team-welcome", title="Team Welcome", level="easy", lesson="Basics",
        statement="<p>Read your team name, then print a welcome message.</p>",
        input_format="One line: the team name.",
        output_format="Two lines: <code>Welcome, &lt;team name&gt;!</code> then <code>Good luck!</code>",
        hint="Use <code>input()</code> to read, and <code>print()</code> twice.",
        starter="# Write your code here\n",
        tests=["Tigers", "Team 5", "PSC", "Falcons"],
        solution='team = input()\nprint("Welcome, " + team + "!")\nprint("Good luck!")\n',
    ),
    dict(
        slug="loud-name", title="Loud Name", level="easy", lesson="Strings",
        statement="<p>Read a name and say hello with the name in CAPITAL letters. Fill the blanks <code>____</code>.</p>",
        input_format="One line: a name.",
        output_format="<code>Hello, &lt;NAME IN CAPITAL LETTERS&gt;</code>",
        hint="Useful: <code>.upper()</code>",
        starter='name = input()\nname = name.____()\nprint("Hello, " + ____)\n',
        tests=["ahmed", "Mona", "omar ali", "sara"],
        solution='name = input()\nname = name.upper()\nprint("Hello, " + name)\n',
    ),
    dict(
        slug="broken-calculator", title="Broken Calculator", level="easy", lesson="Type Conversion & Arithmetic",
        statement="<p>This program should read two numbers and print their sum. But when the input is <code>3</code> and <code>5</code>, it prints <code>Sum: 35</code> instead of <code>Sum: 8</code>. Find the mistake and fix it.</p>",
        input_format="Two lines: two whole numbers.",
        output_format="<code>Sum: &lt;a + b&gt;</code>",
        hint="<code>input()</code> gives text. Convert it to a number first.",
        starter='a = input()\nb = input()\nprint("Sum:", a + b)\n',
        tests=["3\n5", "10\n20", "-4\n4", "100\n250"],
        solution='a = int(input())\nb = int(input())\nprint("Sum:", a + b)\n',
    ),
    dict(
        slug="room-area", title="Room Area", level="easy", lesson="Type Conversion & Arithmetic",
        statement="<p>You want to buy a carpet for your room. Read the length and the width of the room, then print the area.</p><p><b>Area = length x width</b></p>",
        input_format="Two lines: length and width.",
        output_format="<code>Area: &lt;area&gt;</code>",
        hint="Convert the inputs to numbers, then multiply.",
        starter="# Write your code here\n",
        tests=["5\n3", "10\n10", "7\n1", "12\n4"],
        solution='length = int(input())\nwidth = int(input())\nprint("Area:", length * width)\n',
    ),
    dict(
        slug="shopping-discount", title="Shopping Discount", level="easy", lesson="Type Conversion & Arithmetic",
        statement="<p>A shop gives a <b>10% discount</b> on every order. Read the price of one item and the quantity. Calculate the subtotal, the discount and the final price.</p><p><b>Subtotal = price x quantity</b><br><b>Discount = subtotal x 0.10</b><br><b>Final = subtotal - discount</b></p>",
        input_format="Two lines: the price of one item, then the quantity.",
        output_format="Three lines: <code>Subtotal: &lt;subtotal&gt;</code>, <code>Discount: &lt;discount&gt;</code>, <code>Final: &lt;final price&gt;</code>",
        hint="Read the price and the quantity as numbers, then follow the three formulas in order.",
        starter="# Write your code here\n",
        tests=["50\n2", "20\n3", "199\n1", "15\n10", "8\n5"],
        solution='price = float(input())\nquantity = int(input())\nsubtotal = price * quantity\ndiscount = subtotal * 0.10\nfinal = subtotal - discount\nprint("Subtotal:", subtotal)\nprint("Discount:", discount)\nprint("Final:", final)\n',
    ),
    dict(
        slug="phone-battery", title="Phone Battery", level="easy", lesson="Assignment Operators",
        statement="<p>This program reads the battery level, how much the phone was charged, and how much was used. Then it prints the new battery level. The code has <b>2 mistakes</b>. Find them and fix them.</p>",
        input_format="Three lines: battery level, charge amount, used amount.",
        output_format="<code>Battery: &lt;level&gt;%</code>",
        hint="Look carefully at <code>=+</code> and at joining text with a number.",
        starter='battery = int(input())\ncharge = int(input())\nused = int(input())\nbattery =+ charge\nbattery -= used\nprint("Battery: " + battery + "%")\n',
        tests=["40\n30\n25", "10\n50\n20", "90\n10\n100", "0\n0\n0"],
        solution='battery = int(input())\ncharge = int(input())\nused = int(input())\nbattery += charge\nbattery -= used\nprint("Battery: " + str(battery) + "%")\n',
    ),
    dict(
        slug="pass-or-fail", title="Pass or Fail", level="easy", lesson="Decisions",
        statement="<p>Read a student's mark. If the mark is <b>50 or more</b>, print <code>Pass</code>. Otherwise print <code>Fail</code>.</p>",
        input_format="One line: the mark.",
        output_format="<code>Pass</code> or <code>Fail</code>",
        hint="Use <code>if</code> / <code>else</code> with <code>&gt;=</code>.",
        starter="mark = float(input())\n# Write your code here\n",
        tests=["75", "50", "49", "0", "100"],
        solution='mark = float(input())\nif mark >= 50:\n    print("Pass")\nelse:\n    print("Fail")\n',
    ),
    dict(
        slug="baggage-check", title="Baggage Check", level="easy", lesson="Comparison & Logical Operators",
        statement="<p>An airline accepts a passenger's bag when:</p><ul><li>the passenger has a ticket (<code>yes</code>), <b>and</b></li><li>the bag weight is <b>20 kg or less</b>.</li></ul><p>Fill the blanks <code>____</code> to make the code work.</p>",
        input_format="Two lines: has a ticket (<code>yes</code> or <code>no</code>), then the bag weight.",
        output_format="<code>Baggage accepted</code> or <code>Baggage rejected</code>",
        hint="Both conditions must be true: use <code>and</code>. \"20 kg or less\" is <code>&lt;=</code>.",
        starter='ticket = input()\nweight = float(input())\nif ticket == "yes" ____ weight ____ 20:\n    print("Baggage accepted")\nelse:\n    print("Baggage rejected")\n',
        tests=["yes\n18", "yes\n20", "yes\n21", "no\n10", "no\n25"],
        solution='ticket = input()\nweight = float(input())\nif ticket == "yes" and weight <= 20:\n    print("Baggage accepted")\nelse:\n    print("Baggage rejected")\n',
    ),
    dict(
        slug="bigger-number", title="Bigger Number", level="easy", lesson="Decisions",
        statement="<p>Read two whole numbers. Print the bigger one. If the two numbers are the same, print <code>Equal</code>.</p>",
        input_format="Two lines: two whole numbers.",
        output_format="<code>Bigger: &lt;number&gt;</code> or <code>Equal</code>",
        hint="Use <code>if</code>, <code>elif</code>, <code>else</code> with <code>&gt;</code> and <code>&lt;</code>.",
        starter="a = int(input())\nb = int(input())\n# Write your code here\n",
        tests=["3\n9", "10\n2", "5\n5", "-4\n-7", "0\n1"],
        solution='a = int(input())\nb = int(input())\nif a > b:\n    print("Bigger:", a)\nelif b > a:\n    print("Bigger:", b)\nelse:\n    print("Equal")\n',
    ),
    dict(
        slug="age-calculator", title="Age Calculator", level="easy", lesson="Type Conversion & Arithmetic",
        statement="<p>This year is <b>2026</b>. Read the year you were born and print your age.</p>",
        input_format="One line: the birth year.",
        output_format="<code>You are &lt;age&gt; years old</code>",
        hint="age = 2026 - birth year. Example: <code>print(f\"You are {age} years old\")</code>",
        starter="# Write your code here\n",
        tests=["2005", "2000", "1990", "2026", "2015"],
        solution='year = int(input())\nage = 2026 - year\nprint(f"You are {age} years old")\n',
    ),
    # ================= MEDIUM (5) =================
    dict(
        slug="grade-calculator", title="Grade Calculator", level="medium", lesson="Decisions",
        statement="<p>Read a student's score and print the grade:</p><ul><li>90 or more: <code>Excellent</code></li><li>70 or more: <code>Good</code></li><li>50 or more: <code>Pass</code></li><li>less than 50: <code>Fail</code></li></ul>",
        input_format="One line: the score (0 to 100).",
        output_format="<code>Excellent</code>, <code>Good</code>, <code>Pass</code> or <code>Fail</code>",
        hint="Use <code>if</code>, then <code>elif</code> two times, then <code>else</code>. Start with the biggest score.",
        starter="score = float(input())\n# Write your code here\n",
        tests=["95", "90", "75", "70", "55", "50", "30"],
        solution='score = float(input())\nif score >= 90:\n    print("Excellent")\nelif score >= 70:\n    print("Good")\nelif score >= 50:\n    print("Pass")\nelse:\n    print("Fail")\n',
    ),
    dict(
        slug="can-i-drive", title="Can I Drive?", level="medium", lesson="Nested Conditions",
        statement="<p>Read a person's age and if they have a driving license (<code>yes</code> or <code>no</code>).</p><ul><li>Age 18 or more <b>and</b> has a license: <code>You can drive</code></li><li>Age 18 or more <b>but</b> no license: <code>You need a license</code></li><li>Younger than 18: <code>You are too young to drive</code></li></ul>",
        input_format="Two lines: the age, then <code>yes</code> or <code>no</code>.",
        output_format="One of the three messages.",
        hint="Put an <code>if</code> inside another <code>if</code> (nested conditions).",
        starter="age = int(input())\nlicense = input()\n# Write your code here\n",
        tests=["25\nyes", "25\nno", "16\nyes", "18\nyes", "17\nno", "18\nno"],
        solution='age = int(input())\nlicense = input()\nif age >= 18:\n    if license == "yes":\n        print("You can drive")\n    else:\n        print("You need a license")\nelse:\n    print("You are too young to drive")\n',
    ),
    dict(
        slug="countdown-timer", title="Countdown Timer", level="medium", lesson="Loops",
        statement="<p>This program should count down from a number to 1, then print <code>Time's up!</code>. But it never stops! Find the mistake and fix it.</p>",
        input_format="One line: a whole number (0 or more).",
        output_format="The numbers from n down to 1 (one per line), then <code>Time's up!</code>",
        hint="What happens to <code>seconds</code> inside the loop? It must get smaller each time.",
        starter='seconds = int(input())\nwhile seconds > 0:\n    print(seconds)\nprint("Time\'s up!")\n',
        tests=["5", "1", "3", "0", "10"],
        solution='seconds = int(input())\nwhile seconds > 0:\n    print(seconds)\n    seconds -= 1\nprint("Time\'s up!")\n',
    ),
    dict(
        slug="multiplication-table", title="Multiplication Table", level="medium", lesson="Loops",
        statement="<p>Read a number and print its multiplication table from 1 to 10.</p>",
        input_format="One line: a whole number.",
        output_format="10 lines: <code>number x i = result</code> for i from 1 to 10",
        hint="<code>for i in range(1, 11):</code>",
        starter="number = int(input())\n# Write your code here\n",
        tests=["7", "1", "3", "12", "0"],
        solution='number = int(input())\nfor i in range(1, 11):\n    print(number, "x", i, "=", number * i)\n',
    ),
    dict(
        slug="username-generator", title="Username Generator", level="medium", lesson="Strings",
        statement="<p>Read a first name, a last name and a number. Change the names to small letters, then create:</p><ul><li><b>Username</b> = first letter of the first name + last name + number</li><li><b>Email</b> = first name + last name + number + <code>@example.com</code></li></ul><p>Example: Ahmed, Hassan, 25 → username <code>ahassan25</code>, email <code>ahmedhassan25@example.com</code></p>",
        input_format="Three lines: first name, last name, number.",
        output_format="Two lines: <code>Username: &lt;username&gt;</code> then <code>Email: &lt;email&gt;</code>",
        hint="<code>.lower()</code> makes small letters. <code>first[0]</code> is the first letter. Join text with <code>+</code>.",
        starter="# Write your code here\n",
        tests=["Ahmed\nHassan\n25", "MONA\nAli\n7", "sara\nMostafa\n2024", "Omar\nKhaled\n1"],
        solution='first = input().lower()\nlast = input().lower()\nnumber = input()\nusername = first[0] + last + number\nemail = first + last + number + "@example.com"\nprint("Username: " + username)\nprint("Email: " + email)\n',
    ),
    # ================= HARD (5) =================
    dict(
        slug="savings-goal", title="Savings Goal", level="hard", lesson="Loops",
        statement="<p>You start with some savings and add the same amount every month. Keep adding until your savings reach the goal (or more). Print the savings after each month, then the number of months it took.</p><p>Example: start 100, add 50, goal 300 → Month 1: 150, Month 2: 200, Month 3: 250, Month 4: 300.</p>",
        input_format="Three lines: start amount, amount added each month, goal.",
        output_format="One line per month: <code>Month &lt;m&gt;: &lt;savings&gt;</code>, then <code>Goal reached in &lt;months&gt; months</code>",
        hint="Use <code>while savings &lt; goal:</code>, and inside: <code>savings += monthly</code> and <code>months += 1</code>.",
        starter="# Write your code here\n",
        tests=["100\n50\n300", "100\n50\n500", "0\n100\n300", "200\n50\n250", "500\n10\n400", "90\n25\n200"],
        solution='savings = int(input())\nmonthly = int(input())\ngoal = int(input())\nmonths = 0\nwhile savings < goal:\n    savings += monthly\n    months += 1\n    print(f"Month {months}: {savings}")\nprint(f"Goal reached in {months} months")\n',
    ),
    dict(
        slug="atm-transactions", title="ATM Transactions", level="hard", lesson="Mix",
        statement="<p>An ATM starts with your account balance. Then it processes some withdrawal requests. For each request:</p><ul><li>if the amount is <b>less than or equal to</b> the balance: take it from the balance and print <code>Transaction completed</code></li><li>otherwise print <code>Not enough money</code></li></ul><p>At the end print the total money withdrawn and the final balance.</p>",
        input_format="First line: the balance. Second line: the number of requests n. Then n lines: the amount of each request.",
        output_format="One line per request, then <code>Total withdrawn: &lt;total&gt;</code> and <code>Balance: &lt;balance&gt;</code>",
        hint="<code>for i in range(n):</code> reads the requests. Use <code>-=</code> for the balance and <code>+=</code> for the total.",
        starter="# Write your code here\n",
        tests=["1000\n3\n200\n500\n100", "500\n2\n600\n100", "300\n4\n100\n100\n100\n100", "1000\n1\n1000", "50\n3\n60\n70\n80"],
        solution='balance = int(input())\nn = int(input())\ntotal = 0\nfor i in range(n):\n    amount = int(input())\n    if amount <= balance:\n        balance -= amount\n        total += amount\n        print("Transaction completed")\n    else:\n        print("Not enough money")\nprint("Total withdrawn:", total)\nprint("Balance:", balance)\n',
    ),
    dict(
        slug="student-result", title="Student Result", level="hard", lesson="Mix",
        statement="<p>A student has three marks: coursework, midterm and final exam. Calculate the total and the average.</p><p><b>Total = coursework + midterm + final</b><br><b>Average = total / 3</b></p><p>The student passes only when the average is <b>50 or more</b> <b>and</b> the final exam mark is <b>40 or more</b>.</p>",
        input_format="Three lines: coursework, midterm, final exam.",
        output_format="Three lines: <code>Total: &lt;total&gt;</code>, <code>Average: &lt;average&gt;</code>, <code>Result: Pass</code> or <code>Result: Fail</code>",
        hint="Calculate first, then use one <code>if</code> with <code>and</code>.",
        starter="# Write your code here\n",
        tests=["60\n70\n80", "40\n50\n45", "50\n50\n50", "90\n90\n30", "90\n85\n95", "30\n20\n40"],
        solution='coursework = float(input())\nmidterm = float(input())\nfinal = float(input())\ntotal = coursework + midterm + final\naverage = total / 3\nprint(f"Total: {total}")\nprint(f"Average: {average}")\nif average >= 50 and final >= 40:\n    print("Result: Pass")\nelse:\n    print("Result: Fail")\n',
    ),
    dict(
        slug="login-attempts", title="Login Attempts", level="hard", lesson="Loops",
        statement="<p>The password is <code>python123</code>. The user has <b>3 tries</b>.</p><ul><li>Correct password: print <code>Login successful</code> and stop.</li><li>Wrong password: print <code>Wrong password</code>.</li><li>After 3 wrong tries: print <code>Account locked</code>.</li></ul><p>Fill the blanks <code>____</code> to make the code work.</p>",
        input_format="Up to 3 lines: the password tries.",
        output_format="<code>Wrong password</code> / <code>Login successful</code> / <code>Account locked</code>",
        hint="Which word stops a loop? Which operator adds 1 to a variable?",
        starter='tries = 0\nlogged_in = False\nwhile tries ____ 3:\n    password = input()\n    tries ____ 1\n    if password ____ "python123":\n        print("Login successful")\n        logged_in = True\n        ____\n    else:\n        print("Wrong password")\nif logged_in == False:\n    print("Account locked")\n',
        tests=["python123", "abc\npython123", "a\nb\nc", "a\nb\npython123", "x\ny\nz\npython123"],
        solution='tries = 0\nlogged_in = False\nwhile tries < 3:\n    password = input()\n    tries += 1\n    if password == "python123":\n        print("Login successful")\n        logged_in = True\n        break\n    else:\n        print("Wrong password")\nif logged_in == False:\n    print("Account locked")\n',
    ),
    dict(
        slug="shopping-cart", title="Shopping Cart", level="hard", lesson="Mix",
        statement="<p>A customer puts some items in the shopping cart. Read the number of items, then the price of each item. If the total is <b>500 or more</b>, the customer gets a <b>10% discount</b>. Print the total, the discount and the final price.</p><p>Example: items 300 and 250 → total 550 → discount 55 → final 495</p>",
        input_format="First line: the number of items n. Then n lines: the price of each item.",
        output_format="Three lines: <code>Total: &lt;total&gt;</code>, <code>Discount: &lt;discount&gt;</code>, <code>Final: &lt;final price&gt;</code>",
        hint="<code>for i in range(n):</code> reads the prices and adds them with <code>+=</code>. The discount is 0 when the total is less than 500.",
        starter="# Write your code here\n",
        tests=["2\n300\n250", "3\n100\n250\n150", "2\n100\n50", "1\n999", "4\n120\n130\n100\n149", "5\n200\n200\n200\n200\n200"],
        solution='n = int(input())\ntotal = 0\nfor i in range(n):\n    price = float(input())\n    total += price\nif total >= 500:\n    discount = total * 0.10\nelse:\n    discount = 0\nfinal = total - discount\nprint("Total:", total)\nprint("Discount:", discount)\nprint("Final:", final)\n',
    ),
]


class Command(BaseCommand):
    help = "Seed problems, test cases, groups and admin"

    def handle(self, *args, **opts):
        # problems + tests
        per_level = {}
        for i, p in enumerate(PROBLEMS, 1):
            defaults = {k: v for k, v in p.items() if k not in ("tests", "solution", "slug", "starter")}
            defaults["starter_code"] = p["starter"]
            per_level[p["level"]] = per_level.get(p["level"], 0) + 1
            defaults["seq"], defaults["order"] = i, per_level[p["level"]]
            prob, created = Problem.objects.update_or_create(
                slug=p["slug"], defaults=defaults,
            )
            prob.tests.all().delete()
            for j, inp in enumerate(p["tests"]):
                exp = expected_output(p["solution"], inp)
                TestCase.objects.create(
                    problem=prob, input_text=inp, expected_output=exp,
                    is_sample=(j == 0), order=j,
                )
            self.stdout.write(f"  {'+' if created else '~'} {prob} ({len(p['tests'])} tests)")

        # problems that are no longer in the list (and their submissions)
        old = Problem.objects.exclude(slug__in=[p["slug"] for p in PROBLEMS])
        for prob in old:
            self.stdout.write(f"  - removed {prob.title}")
        old.delete()

        # groups: only on a fresh database, so renamed groups are never duplicated
        if not Group.objects.exists():
            for i in range(1, 6):
                pw = secrets.token_hex(3)
                g = Group(name=f"Group {i}")
                g.set_password(pw)
                g.save()
                self.stdout.write(f"  group created: {g.name} / {pw}")
        else:
            self.stdout.write("  groups already exist - left unchanged")

        # admin staff user for dashboard
        if not User.objects.filter(username="admin").exists():
            pw = os.environ.get("ADMIN_PASSWORD") or secrets.token_urlsafe(9)
            User.objects.create_superuser("admin", "admin@unity.edu", pw)
            self.stdout.write(f"  admin user created (admin / {pw})")

        Contest.get()
        self.stdout.write(self.style.SUCCESS("Seed complete."))
