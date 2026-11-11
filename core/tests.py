import io
import time

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

from . import runner
from .management.commands.seed import PROBLEMS
from .models import Contest, Group, Problem, Submission


class RunnerTests(TestCase):
    def test_plain_program(self):
        r = runner.run_code("print(input()[::-1])", "abc")
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["out"].strip(), "cba")

    def test_timeout(self):
        r = runner.run_code("while True: pass", "", timeout=1)
        self.assertEqual(r["status"], "timeout")

    def test_output_flood_is_capped(self):
        start = time.monotonic()
        r = runner.run_code("while True: print(1)", "")
        self.assertLess(time.monotonic() - start, 3)
        self.assertIn("Output limit", r["err"])
        self.assertLessEqual(len(r["out"]), runner.MAX_OUTPUT)

    def test_blocked_code(self):
        for code in ["import os", "open('x')", "().__class__", "__builtins__", "import subprocess"]:
            self.assertIsNotNone(runner.check_code(code), code)
            self.assertEqual(runner.run_code(code, "")["status"], "blocked")

    def test_allowed_code(self):
        for code in ['if __name__ == "__main__": print(1)', "x = f'{3.14159:.2f}'", "import math",
                     "name = input()\nname = name.____()\nprint(____)"]:
            self.assertIsNone(runner.check_code(code), code)

    def test_input_prompt_is_not_printed(self):
        r = runner.run_code('name = input("Enter your name: ")\nprint("Welcome", name)', "Ahmed")
        self.assertEqual(r["out"].strip(), "Welcome Ahmed")

    def test_error_traceback_shows_only_student_lines(self):
        r = runner.run_code("x = 1\nprint(x / 0)", "")
        self.assertIn('line 2', r["err"])
        self.assertIn("ZeroDivisionError", r["err"])
        self.assertNotIn("exec(", r["err"])
        self.assertEqual(runner.run_code("print(input())", "")["returncode"], 1)

    def test_numbers_compare_by_value(self):
        m = runner.outputs_match
        self.assertTrue(m("Total: 120.0\n", "Total: 120\n"))
        self.assertTrue(m("Final: 495.00000000000006", "Final: 495.0"))
        self.assertTrue(m("Battery: 45.0%", "Battery: 45%"))
        self.assertFalse(m("Total: 121", "Total: 120"))
        self.assertFalse(m("total: 120", "Total: 120"))
        self.assertFalse(m("Total:120", "Total: 120"))
        self.assertFalse(m("Average: 66.67", "Average: 66.66666666666667"))
        self.assertFalse(m("1\n2", "1\n2\n3"))

    def test_unicode_io(self):
        r = runner.run_code("print(input())", "مرحبا")
        self.assertEqual(r["out"].strip(), "مرحبا")


class ContestFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("seed", stdout=io.StringIO())
        cls.group = Group.objects.first()
        cls.group.set_password("pw")
        cls.group.save()
        User.objects.create_superuser("boss", "b@x.com", "bosspw")

    def setUp(self):
        cache.clear()
        self.c = self.client
        self.c.post("/login/", {"username": self.group.name, "password": "pw"})

    def start(self):
        c = Contest.get()
        c.started_at = timezone.now()
        c.save()

    def test_all_reference_solutions_accepted(self):
        for p in PROBLEMS:
            prob = Problem.objects.get(slug=p["slug"])
            tests = list(prob.tests.all())
            verdict, _, _ = runner.judge(p["solution"], tests)
            self.assertEqual(verdict, "accepted", p["slug"])
            verdict, _, _ = runner.judge(p["starter"], tests)
            self.assertNotEqual(verdict, "accepted", p["slug"] + " starter must not pass")
        seqs = list(Problem.objects.values_list("seq", flat=True))
        self.assertEqual(seqs, list(range(1, len(PROBLEMS) + 1)))

    def test_problems_hidden_before_start(self):
        r = self.c.get("/problems/")
        self.assertContains(r, "has not started")
        self.assertNotContains(r, "Team Welcome")
        self.assertRedirects(self.c.get("/problem/team-welcome/"), "/problems/")
        self.assertEqual(self.c.post("/problem/team-welcome/run/", {"code": "print(1)"}).status_code, 403)
        self.assertEqual(self.c.post("/problem/team-welcome/submit/", {"code": "print(1)"}).status_code, 403)

    @override_settings(SUBMIT_COOLDOWN_SECONDS=60)
    def test_submit_accept_and_cooldown(self):
        self.start()
        self.assertContains(self.c.get("/problems/"), "Team Welcome")
        sol = PROBLEMS[0]["solution"]
        r = self.c.post("/problem/team-welcome/submit/", {"code": sol}).json()
        self.assertEqual(r["verdict"], "accepted")
        r = self.c.post("/problem/team-welcome/submit/", {"code": sol})
        self.assertEqual(r.status_code, 429)
        self.assertEqual(Submission.objects.count(), 1)
        rows = self.c.get("/api/leaderboard/").json()["rows"]
        self.assertEqual(next(x for x in rows if x["name"] == self.group.name)["solved"], 1)

    def test_submit_after_end_rejected(self):
        c = Contest.get()
        c.started_at = timezone.now() - timezone.timedelta(seconds=c.duration_seconds + 5)
        c.save()
        r = self.c.post("/problem/team-welcome/submit/", {"code": "print(1)"})
        self.assertEqual(r.status_code, 403)

    def test_code_too_long(self):
        self.start()
        r = self.c.post("/problem/team-welcome/run/", {"code": "#" * 30000})
        self.assertEqual(r.status_code, 400)

    def test_api_requires_login(self):
        self.c.get("/logout/")
        self.assertEqual(self.c.post("/problem/team-welcome/submit/", {"code": "x"}).status_code, 401)

    def test_admin_pages(self):
        a = self.client_class()
        a.post("/login/", {"username": "boss", "password": "bosspw"})
        for url in ["/dashboard/", "/groups/", "/leaderboard/"]:
            self.assertEqual(a.get(url).status_code, 200, url)
        a.post("/api/contest-action/", {"action": "simulate"})
        self.assertEqual(Submission.objects.count(), 0)

    def test_old_group_hash_is_upgraded_on_login(self):
        from django.contrib.auth.hashers import make_password
        self.group.password = make_password("old")
        self.group.save()
        self.c.get("/logout/")
        r = self.c.post("/login/", {"username": self.group.name, "password": "old"})
        self.assertRedirects(r, "/problems/", fetch_redirect_response=False)
        self.group.refresh_from_db()
        self.assertTrue(self.group.password.startswith("pbkdf2_sha256_group$"))

    def test_login_lockout_after_wrong_passwords(self):
        self.c.get("/logout/")
        for _ in range(5):
            self.assertEqual(self.c.post("/login/", {"username": self.group.name, "password": "bad"}).status_code, 401)
        r = self.c.post("/login/", {"username": self.group.name, "password": "pw"})
        self.assertEqual(r.status_code, 429)
        # another device (IP) can still log in as the same group
        other = self.client_class(REMOTE_ADDR="10.0.0.9")
        r = other.post("/login/", {"username": self.group.name, "password": "pw"})
        self.assertRedirects(r, "/problems/", fetch_redirect_response=False)

    def test_ip_lockout_for_spraying(self):
        self.c.get("/logout/")
        for i in range(30):
            self.c.post("/login/", {"username": f"guess{i}", "password": "x"})
        r = self.c.post("/login/", {"username": self.group.name, "password": "pw"})
        self.assertEqual(r.status_code, 429)

    def test_password_change_logs_out_devices(self):
        self.start()
        self.assertEqual(self.c.get("/problems/").status_code, 200)
        a = self.client_class()
        a.post("/login/", {"username": "boss", "password": "bosspw"})
        a.post("/api/group-action/", {"action": "update_group", "group_id": self.group.pk,
                                      "name": self.group.name, "password": "newpw"})
        self.assertRedirects(self.c.get("/problems/"), "/login/", fetch_redirect_response=False)

    def test_kick_devices(self):
        self.start()
        self.c.get("/problems/")
        a = self.client_class()
        a.post("/login/", {"username": "boss", "password": "bosspw"})
        self.assertContains(a.get("/groups/"), "Devices online: <b>1</b>")
        a.post("/api/group-action/", {"action": "kick_devices", "group_id": self.group.pk})
        self.assertRedirects(self.c.get("/problems/"), "/login/", fetch_redirect_response=False)
        self.assertEqual(self.c.post("/problem/team-welcome/run/", {"code": "x"}).status_code, 401)

    def test_admin_path_hidden_and_login_rate_limited(self):
        self.assertEqual(self.client_class().get("/admin/").status_code, 404)
        r = self.client_class().get("/psc-control/")
        self.assertIn("/login/", r["Location"])
        a = self.client_class()
        r = a.post("/login/?next=/psc-control/", {"username": "boss", "password": "bosspw"})
        self.assertRedirects(r, "/psc-control/", fetch_redirect_response=False)
        self.assertEqual(a.get("/psc-control/").status_code, 200)
        r = self.client_class().post("/login/?next=https://evil.com/", {"username": "boss", "password": "bosspw"})
        self.assertRedirects(r, "/dashboard/", fetch_redirect_response=False)

    def test_dashboard_redirects_non_staff_to_login(self):
        r = self.client_class().get("/dashboard/")
        self.assertTrue(r["Location"].startswith("/login/"))

    def test_run_throttle(self):
        self.start()
        self.assertEqual(self.c.post("/problem/team-welcome/run/", {"code": "print(1)"}).status_code, 200)
        self.assertEqual(self.c.post("/problem/team-welcome/run/", {"code": "print(1)"}).status_code, 429)

    def _solve(self, group, problems, elapsed):
        for p in problems:
            Submission.objects.create(group=group, problem=p, code="x", status="accepted", contest_elapsed=elapsed)
        cache.clear()

    def test_results_hidden_until_time_is_up(self):
        self.start()
        probs = list(Problem.objects.all())
        other = Group.objects.exclude(pk=self.group.pk).first()
        self._solve(self.group, probs, 100)
        self._solve(other, probs[:3], 50)
        d = self.c.get("/api/status/").json()
        self.assertEqual(d["me"]["solved"], len(probs))
        self.assertEqual(d["total"], len(probs))
        self.assertNotIn("results", d)

        c = Contest.get()
        c.started_at = timezone.now() - timezone.timedelta(seconds=c.duration_seconds + 1)
        c.save()
        d = self.c.get("/api/status/").json()
        self.assertEqual(d["state"], "ended")
        self.assertEqual(d["results"]["winner"], self.group.name)
        self.assertEqual(d["me"]["rank"], 1)
        self.assertEqual([p["name"] for p in d["results"]["podium"]], [self.group.name, other.name])

    def test_tie_goes_to_who_reached_it_first(self):
        self.start()
        probs = list(Problem.objects.all())[:5]
        other = Group.objects.exclude(pk=self.group.pk).first()
        self._solve(self.group, probs, 900)
        self._solve(other, probs, 300)
        c = Contest.get()
        c.started_at = timezone.now() - timezone.timedelta(seconds=c.duration_seconds + 1)
        c.save()
        d = self.c.get("/api/status/").json()
        self.assertEqual(d["results"]["winner"], other.name)
        self.assertEqual(d["me"]["rank"], 2)

    def test_results_screen_admin_only(self):
        self.assertNotEqual(self.c.get("/results/").status_code, 200)
        a = self.client_class()
        a.post("/login/", {"username": "boss", "password": "bosspw"})
        self.assertEqual(a.get("/results/").status_code, 200)
        self.assertEqual(a.get("/api/status/").status_code, 200)

    def test_seed_does_not_duplicate_groups(self):
        self.group.name = "Renamed"
        self.group.save()
        n = Group.objects.count()
        call_command("seed", stdout=io.StringIO())
        self.assertEqual(Group.objects.count(), n)
