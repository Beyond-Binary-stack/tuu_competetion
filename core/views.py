import logging

from django.conf import settings
from django.contrib import messages
from django.core.cache import cache
from django.db.models import Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.http import JsonResponse
from urllib.parse import urlencode

from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.utils.http import url_has_allowed_host_and_scheme

from .models import Contest, Group, Problem, SavedCode, Submission
from . import runner, security

SESSION_GROUP = "group_id"
SESSION_GROUP_VERSION = "group_ver"
RUN_COOLDOWN_SECONDS = 2
STATS_CACHE_KEY = "group_stats"
STATS_CACHE_SECONDS = 2
MAX_CODE_LENGTH = 20000

log = logging.getLogger("contest")


def _invalidate_stats():
    cache.delete(STATS_CACHE_KEY)


def current_group(request):
    if hasattr(request, "_group"):
        return request._group
    group = None
    gid = request.session.get(SESSION_GROUP)
    if gid:
        group = Group.objects.filter(pk=gid).first()
        if group and group.session_version != request.session.get(SESSION_GROUP_VERSION):
            group = None  # logged out by the admin (password changed / devices kicked)
        if group is None:
            request.session.pop(SESSION_GROUP, None)
            request.session.pop(SESSION_GROUP_VERSION, None)
        else:
            security.touch_device(group.pk, request.session.session_key, security.client_ip(request))
    request._group = group
    return group


def is_staff_user(user):
    return user.is_authenticated and user.is_staff


def home(request):
    if request.user.is_authenticated and request.user.is_staff:
        return redirect("dashboard")
    if current_group(request):
        return redirect("problems")
    return redirect("login")


def _safe_next(request):
    nxt = request.GET.get("next", "")
    if nxt and url_has_allowed_host_and_scheme(nxt, allowed_hosts={request.get_host()}, require_https=request.is_secure()):
        return nxt
    return None


def login_view(request):
    error = None
    status = 200
    if request.method == "POST":
        username = request.POST.get("username", "").strip()[:100]
        password = request.POST.get("password", "")[:200]
        ip = security.client_ip(request)

        locked = security.login_locked_seconds(ip, username)
        if locked:
            minutes = max(1, round(locked / 60))
            log.warning("login locked ip=%s name=%r (%ss left)", ip, username, locked)
            return render(request, "core/login.html", {
                "error": f"Too many wrong attempts. Try again in {minutes} minute(s) or ask the organizers.",
            }, status=429)

        # Check groups first: it avoids an expensive staff hash check on every team login.
        group = Group.objects.filter(name__iexact=username).first()
        if group:
            if group.check_password(password):
                security.clear_login_failures(ip, username)
                request.session.cycle_key()
                request.session[SESSION_GROUP] = group.pk
                request.session[SESSION_GROUP_VERSION] = group.session_version
                log.info("group login name=%s ip=%s", group.name, ip)
                return redirect("problems")
        else:
            user = authenticate(request, username=username, password=password)
            if user and user.is_staff:
                security.clear_login_failures(ip, username)
                auth_login(request, user)
                log.info("staff login name=%s ip=%s", user.username, ip)
                return redirect(_safe_next(request) or "dashboard")
        security.register_login_failure(ip, username)
        log.warning("failed login ip=%s name=%r", ip, username)
        error = "Wrong username or password."
        status = 401
    return render(request, "core/login.html", {"error": error}, status=status)


def admin_login_redirect(request):
    """Send Django-admin logins through the rate-limited contest login."""
    if is_staff_user(request.user):
        return redirect(_safe_next(request) or "admin:index")
    nxt = _safe_next(request)
    url = reverse("login")
    return redirect(f"{url}?{urlencode({'next': nxt})}" if nxt else url)


def logout_view(request):
    request.session.pop(SESSION_GROUP, None)
    request.session.pop(SESSION_GROUP_VERSION, None)
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect("login")


def group_required(view):
    def wrapper(request, *a, **kw):
        if not current_group(request):
            return redirect("login")
        return view(request, *a, **kw)
    return wrapper


def any_user_required(view):
    def wrapper(request, *a, **kw):
        if current_group(request) or is_staff_user(request.user):
            return view(request, *a, **kw)
        return redirect("login")
    return wrapper


def _problem_status_map(group):
    """problem_id -> {"solved": bool, "tries": int, "solved_elapsed": int|None}"""
    data = {}
    subs = Submission.objects.filter(group=group).order_by("created_at")
    first_accept = {}
    for s in subs:
        d = data.setdefault(s.problem_id, {"solved": False, "tries": 0, "solved_elapsed": None})
        d["tries"] += 1
        if s.status == Submission.Status.ACCEPTED and not d["solved"]:
            d["solved"] = True
            d["solved_elapsed"] = s.contest_elapsed
    return data


@group_required
def problem_list(request):
    group = current_group(request)
    contest = Contest.get()
    problems = Problem.objects.all()
    if contest.state_label() == "not_started":
        return render(request, "core/problems.html", {
            "group": group, "contest": contest, "lessons": [], "waiting": True,
            "solved_count": 0, "total": problems.count(),
        })
    status = _problem_status_map(group)

    lessons = {}
    for p in problems:
        st = status.get(p.id, {"solved": False, "tries": 0, "solved_elapsed": None})
        lessons.setdefault(p.lesson, []).append({
            "problem": p, "status": st,
        })
    lesson_order = ["Basics", "Strings", "Type Conversion & Arithmetic", "Assignment Operators",
                    "Comparison & Logical Operators", "Decisions", "Nested Conditions", "Loops", "Mix"]
    ordered = sorted(lessons.items(), key=lambda kv: (lesson_order.index(kv[0]) if kv[0] in lesson_order else 99, kv[0]))
    return render(request, "core/problems.html", {
        "group": group, "contest": contest, "lessons": ordered,
        "solved_count": sum(1 for v in status.values() if v["solved"]),
        "total": problems.count(),
    })


@group_required
def problem_detail(request, slug):
    group = current_group(request)
    if Contest.get().state_label() == "not_started":
        return redirect("problems")
    problem = get_object_or_404(Problem.objects.prefetch_related("tests"), slug=slug)
    saved = SavedCode.objects.filter(group=group, problem=problem).first()
    status = _problem_status_map(group).get(problem.id, {"solved": False, "tries": 0})
    sample = problem.sample_test
    return render(request, "core/problem_detail.html", {
        "group": group, "problem": problem, "contest": Contest.get(),
        "saved_code": saved.code if saved else problem.starter_code,
        "status": status,
        "sample_input": sample.input_text if sample else "",
        "sample_output": sample.expected_output if sample else "",
    })


def _get_problem_and_group(request, slug):
    group = current_group(request)
    if not group:
        return None, None, JsonResponse({"error": "not_logged_in"}, status=401)
    problem = get_object_or_404(Problem.objects.prefetch_related("tests"), slug=slug)
    if len(request.POST.get("code", "")) > MAX_CODE_LENGTH:
        return None, None, JsonResponse({"error": "Your code is too long."}, status=400)
    if Contest.get().state_label() == "not_started":
        return None, None, JsonResponse({"error": "contest_not_open", "state": "not_started"}, status=403)
    return group, problem, None


def _busy_response():
    return JsonResponse({"error": "The judge is busy right now. Please try again in a few seconds."}, status=503)


def group_required_api(view):
    def wrapper(request, *a, **kw):
        if not current_group(request):
            return JsonResponse({"error": "not_logged_in"}, status=401)
        return view(request, *a, **kw)
    return wrapper


@group_required_api
@require_POST
def run_sample(request, slug):
    group, problem, err = _get_problem_and_group(request, slug)
    if err:
        return err
    if not cache.add(f"run-cooldown:{group.pk}", 1, RUN_COOLDOWN_SECONDS):
        return JsonResponse({"error": "Please wait a moment before running again."}, status=429)
    code = request.POST.get("code", "")
    sample = problem.sample_test
    if not sample:
        return JsonResponse({"error": "no sample"}, status=400)
    r = runner.run_code(code, sample.input_text)
    if r["status"] == "busy":
        return _busy_response()
    payload = {
        "status": r["status"],
        "out": r["out"],
        "err": r["err"],
        "expected": sample.expected_output,
        "input": sample.input_text,
        "passed": r["status"] == "ok" and r.get("returncode", 0) == 0
                  and runner.outputs_match(r["out"], sample.expected_output),
    }
    return JsonResponse(payload)


@group_required_api
@require_POST
def save_code(request, slug):
    group, problem, err = _get_problem_and_group(request, slug)
    if err:
        return err
    code = request.POST.get("code", "")
    SavedCode.objects.update_or_create(group=group, problem=problem, defaults={"code": code})
    return JsonResponse({"ok": True})


@group_required_api
@require_POST
def submit_code(request, slug):
    group, problem, err = _get_problem_and_group(request, slug)
    if err:
        return err
    contest = Contest.get()
    if not contest.is_open():
        return JsonResponse({"error": "contest_not_open", "state": contest.state_label()}, status=403)

    cooldown = settings.SUBMIT_COOLDOWN_SECONDS
    last = Submission.objects.filter(group=group).order_by("-created_at").values_list("created_at", flat=True).first()
    if last and (timezone.now() - last).total_seconds() < cooldown:
        return JsonResponse({"error": f"Please wait {cooldown} seconds between submissions."}, status=429)

    code = request.POST.get("code", "")
    SavedCode.objects.update_or_create(group=group, problem=problem, defaults={"code": code})

    verdict, results, first_bad = runner.judge(code, list(problem.tests.all()))
    if verdict == "busy":
        return _busy_response()
    contest.refresh_from_db()
    elapsed = min(contest.elapsed_seconds(), contest.duration_seconds)

    # throttle: one submission record per judge call
    Submission.objects.create(
        group=group, problem=problem, code=code,
        status=verdict if verdict != "accepted" else Submission.Status.ACCEPTED,
        detail={"tests": results[:10]},
        contest_elapsed=elapsed,
    )
    _invalidate_stats()
    log.info("submit group=%s problem=%s verdict=%s elapsed=%s", group.name, problem.slug, verdict, elapsed)

    payload = {"verdict": verdict, "tests": results, "elapsed": elapsed}
    if verdict == "accepted":
        payload["message"] = "Accepted!"
    elif verdict == "wrong" and first_bad:
        payload["wrong"] = first_bad
    elif verdict == "error" and first_bad:
        payload["error"] = first_bad.get("err", "")
        payload["out"] = first_bad.get("out", "")
    elif verdict == "timeout":
        payload["message"] = "Time Limit Exceeded (3 seconds)"
    elif verdict == "blocked":
        payload["message"] = "Blocked: " + first_bad.get("reason", "")
    return JsonResponse(payload)


def _group_stats():
    """Return list of dicts for leaderboard (cached for a couple of seconds)."""
    cached = cache.get(STATS_CACHE_KEY)
    if cached is None:
        cached = _compute_group_stats()
        cache.set(STATS_CACHE_KEY, cached, STATS_CACHE_SECONDS)
    return cached


def _compute_group_stats():
    groups = Group.objects.all()
    problems = list(Problem.objects.all())
    # first accepted submission per (group, problem)
    first_accept = {}
    accepted = (Submission.objects.filter(status=Submission.Status.ACCEPTED)
                .order_by("created_at").values_list("group_id", "problem_id", "contest_elapsed"))
    for gid, pid, elapsed in accepted:
        first_accept.setdefault((gid, pid), elapsed)
    tries_by_group = dict(Submission.objects.values("group_id").annotate(n=Count("id")).values_list("group_id", "n"))
    rows = []
    for g in groups:
        solved_times = sorted(
            first_accept.get((g.id, p.id)) for p in problems
            if (g.id, p.id) in first_accept
        )
        solved_times = [t for t in solved_times if t is not None]
        tries = tries_by_group.get(g.id, 0)
        # time to reach current solved count = the count-th smallest solve time
        reach_time = solved_times[len(solved_times) - 1] if solved_times else None
        per_level = {lvl: 0 for lvl, _ in Problem.Level.choices}
        for p in problems:
            if (g.id, p.id) in first_accept:
                per_level[p.level] += 1
        rows.append({
            "group": g,
            "solved": len(solved_times),
            "pct": round(len(solved_times) / len(problems) * 100) if problems else 0,
            "reach_time": reach_time,
            "tries": tries,
            "per_level": per_level,
            "solved_times": solved_times,
        })
    rows.sort(key=lambda r: (-r["solved"], r["reach_time"] if r["reach_time"] is not None else 10**9))
    return rows, problems


@any_user_required
def leaderboard(request):
    rows, problems = _group_stats()
    contest = Contest.get()
    return render(request, "core/leaderboard.html", {
        "rows": rows, "problems": problems, "contest": contest,
        "is_admin": False, "group": current_group(request),
    })


@user_passes_test(is_staff_user)
def dashboard(request):
    rows, problems = _group_stats()
    contest = Contest.get()
    all_subs = Submission.objects.select_related("group", "problem").order_by("-created_at")[:50]
    total_subs = Submission.objects.count()
    accepted = Submission.objects.filter(status=Submission.Status.ACCEPTED).count()
    solves = sum(r["solved"] for r in rows)
    possible = len(rows) * len(problems)
    stats = {
        "groups": len(rows),
        "solves": solves,
        "possible": possible,
        "submissions": total_subs,
        "accepted": accepted,
        "accept_rate": round(accepted / total_subs * 100) if total_subs else 0,
        "contest_pct": max(0, min(100, round(contest.elapsed_seconds() / contest.duration_seconds * 100))),
    }
    rows = [dict(r, devices=len(security.online_devices(r["group"].pk))) for r in rows]
    return render(request, "core/dashboard.html", {
        "rows": rows, "top_rows": rows[:5], "problems": problems, "contest": contest,
        "recent": all_subs, "groups": Group.objects.all(), "stats": stats,
        "debug": settings.DEBUG,
    })


@user_passes_test(is_staff_user)
def groups_manage(request):
    groups = [{"g": g, "devices": security.online_devices(g.pk)} for g in Group.objects.all()]
    return render(request, "core/groups.html", {"groups": groups})


@user_passes_test(is_staff_user)
@require_POST
def contest_action(request):
    contest = Contest.get()
    action = request.POST.get("action")
    now = timezone.now()
    if action == "start":
        if not contest.started_at:
            contest.started_at = now
        contest.paused_seconds = 0
        contest.paused_at = None
        contest.save()
    elif action == "pause":
        if contest.started_at and not contest.is_paused:
            contest.paused_at = now
            contest.save()
    elif action == "resume":
        if contest.is_paused:
            contest.paused_seconds += int((now - contest.paused_at).total_seconds())
            contest.paused_at = None
            contest.save()
    elif action == "reset":
        # clear all submissions & saved code and wait for manual start
        Submission.objects.all().delete()
        SavedCode.objects.all().delete()
        contest.started_at = None
        contest.paused_seconds = 0
        contest.paused_at = None
        contest.save()
    elif action == "duration":
        try:
            mins = int(request.POST.get("minutes", 180))
            contest.duration_seconds = max(60, mins * 60)
            contest.save()
        except ValueError:
            pass
    elif action == "simulate" and settings.DEBUG:
        _simulate(contest.elapsed_seconds())
    _invalidate_stats()
    log.info("contest action=%s by=%s", action, request.user.username)
    return redirect("dashboard")


@user_passes_test(is_staff_user)
@require_POST
def group_action(request):
    action = request.POST.get("action")

    if action == "add_group":
        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "")
        if not name or not password:
            messages.error(request, "Group name and password are required.")
        elif Group.objects.filter(name__iexact=name).exists():
            messages.error(request, "A group with that name already exists.")
        else:
            group = Group(name=name[:100])
            group.set_password(password)
            group.save()
            messages.success(request, f"Group '{group.name}' created.")

    elif action == "update_group":
        try:
            group = Group.objects.get(pk=request.POST.get("group_id"))
        except (Group.DoesNotExist, TypeError, ValueError):
            group = None
        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "")
        if not group:
            messages.error(request, "Group not found.")
        elif not name:
            messages.error(request, "Group name cannot be empty.")
        elif Group.objects.filter(name__iexact=name).exclude(pk=group.pk).exists():
            messages.error(request, "Another group already uses that name.")
        else:
            group.name = name[:100]
            if password:
                group.set_password(password)
                group.session_version += 1
                security.forget_devices(group.pk)
            group.save()
            log.info("group updated name=%s password_changed=%s", group.name, bool(password))
            messages.success(request, f"Group '{group.name}' updated."
                             + (" All its devices were logged out." if password else ""))

    elif action == "kick_devices":
        group = Group.objects.filter(pk=request.POST.get("group_id") or 0).first()
        if group:
            group.session_version += 1
            group.save(update_fields=["session_version"])
            security.forget_devices(group.pk)
            log.info("devices logged out for group=%s", group.name)
            messages.success(request, f"All devices of '{group.name}' were logged out.")

    elif action == "change_admin_password":
        password = request.POST.get("password", "")
        confirm = request.POST.get("confirm", "")
        if not password:
            messages.error(request, "Password cannot be empty.")
        elif password != confirm:
            messages.error(request, "Passwords do not match.")
        else:
            request.user.set_password(password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Admin password updated.")

    _invalidate_stats()
    return redirect("groups_manage")


def _simulate(elapsed):
    import random
    groups = list(Group.objects.all())
    problems = list(Problem.objects.all())
    for g in groups:
        n = random.randint(3, len(problems))
        chosen = random.sample(problems, min(n, len(problems)))
        for i, p in enumerate(chosen):
            t = int(elapsed * random.uniform(0.15, 0.95))
            Submission.objects.get_or_create(
                group=g, problem=p,
                defaults={
                    "code": "# simulated",
                    "status": Submission.Status.ACCEPTED,
                    "detail": {},
                    "contest_elapsed": t,
                },
            )


@any_user_required
def api_leaderboard(request):
    rows, problems = _group_stats()
    contest = Contest.get()
    group = current_group(request)
    status_map = _problem_status_map(group) if group else {}
    data = {
        "contest": {
            "state": contest.state_label(),
            "remaining": contest.remaining_seconds(),
            "elapsed": contest.elapsed_seconds(),
        },
        "rows": [
            {
                "name": r["group"].name,
                "solved": r["solved"],
                "reach_time": r["reach_time"],
                "tries": r["tries"],
                "per_level": r["per_level"],
            } for r in rows
        ],
        "problems": [
            {
                "id": p.id,
                "title": p.title,
                "level": p.level,
                "slug": p.slug,
                "solved": status_map.get(p.id, {}).get("solved", False),
                "tries": status_map.get(p.id, {}).get("tries", 0),
            } for p in problems
        ],
    }
    return JsonResponse(data)


def _podium(rows):
    """Final ranking for the results screens: groups that solved at least one problem."""
    return [
        {"rank": i, "name": r["group"].name, "solved": r["solved"], "reach_time": r["reach_time"]}
        for i, r in enumerate((r for r in rows if r["solved"] > 0), 1)
    ]


@any_user_required
def api_status(request):
    """Small status endpoint polled by every page for the 'finished' / winner screens.
    Final results are only revealed once the contest time is over."""
    contest = Contest.get()
    state = contest.state_label()
    rows, problems = _group_stats()
    data = {
        "state": state,
        "remaining": contest.remaining_seconds(),
        "round": contest.started_at.isoformat() if contest.started_at else "",
        "total": len(problems),
    }
    group = current_group(request)
    if group:
        mine = next((r for r in rows if r["group"].pk == group.pk), None)
        data["me"] = {"name": group.name, "solved": mine["solved"] if mine else 0}
    if state == "ended":
        podium = _podium(rows)
        data["results"] = {"podium": podium[:3], "winner": podium[0]["name"] if podium else None}
        if group:
            data["me"]["rank"] = next((p["rank"] for p in podium if p["name"] == group.name), None)
    return JsonResponse(data)


@user_passes_test(is_staff_user)
def results_screen(request):
    return render(request, "core/results.html", {"contest": Contest.get()})
