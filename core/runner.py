"""Safe-ish execution of student code for the contest."""
import ast
import os
import re
import subprocess
import sys
import tempfile
import threading

from django.conf import settings

TIMEOUT_SECONDS = 3
MAX_OUTPUT = 20000
# How long a request waits for a free judge slot before giving up.
SLOT_WAIT_SECONDS = 30
MEMORY_LIMIT_BYTES = 512 * 1024 * 1024

BANNED_MODULES = {
    "os", "sys", "subprocess", "socket", "shutil", "pathlib", "io",
    "builtins", "ctypes", "pickle", "marshal", "importlib", "runpy",
    "signal", "threading", "multiprocessing", "pty", "fcntl",
    "resource", "gc", "inspect", "code", "codeop", "asyncio", "urllib",
    "http", "ftplib", "smtplib", "tempfile", "glob", "webbrowser", "_thread",
}
BANNED_CALLS = {
    "open", "exec", "eval", "compile", "__import__", "globals", "locals",
    "vars", "getattr", "setattr", "delattr", "breakpoint", "help",
}
BANNED_ATTRS = {"system", "popen", "spawn", "fork", "kill", "remove", "unlink", "rmdir"}
ALLOWED_DUNDERS = {"__name__", "__init__", "__str__", "__repr__"}

_slots = threading.BoundedSemaphore(getattr(settings, "JUDGE_CONCURRENCY", 4))

# Runs inside the child interpreter before the student's code:
# - on POSIX, applies OS resource limits (avoids preexec_fn, unsafe with threads)
# - replaces input() so the prompt text (input("Enter x: ")) is NOT printed;
#   students learn to write prompts, and they must not break the expected output
# - hides this launcher's own frame from tracebacks
_LAUNCHER = f"""
import os, sys, builtins
if os.name == "posix":
    import resource as r
    for k, v in ((r.RLIMIT_AS, {MEMORY_LIMIT_BYTES}), (r.RLIMIT_CPU, {TIMEOUT_SECONDS + 2}),
                 (r.RLIMIT_FSIZE, 1048576), (r.RLIMIT_CORE, 0)):
        try:
            r.setrlimit(k, (v, v))
        except (ValueError, OSError):
            pass
def _quiet_input(prompt=""):
    line = sys.stdin.readline()
    if not line:
        raise EOFError("EOF when reading a line")
    return line[:-1] if line.endswith("\\n") else line
builtins.input = _quiet_input
_src = sys.argv[1]
del os, builtins, _quiet_input
try:
    exec(compile(_src, "main.py", "exec"), {{"__name__": "__main__"}})
except SystemExit:
    raise
except BaseException as e:
    import traceback
    traceback.print_exception(type(e), e, e.__traceback__.tb_next)
    sys.exit(1)
"""


def _is_dunder(name):
    # "____" (the fill-in-the-blank marker) is not a dunder
    return (name.startswith("__") and name.endswith("__") and name.strip("_") != ""
            and name not in ALLOWED_DUNDERS)


def check_code(code: str):
    """Return None if allowed, else a short reason string."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None  # syntax errors are fine - they just fail at runtime

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for a in node.names:
                if a.name.split(".")[0] in BANNED_MODULES:
                    return f"import {a.name} is not allowed"
        elif isinstance(node, ast.ImportFrom):
            if (node.module or "").split(".")[0] in BANNED_MODULES:
                return f"import from {node.module} is not allowed"
        elif isinstance(node, ast.Call):
            f = node.func
            name = None
            if isinstance(f, ast.Name):
                name = f.id
            elif isinstance(f, ast.Attribute):
                name = f.attr
            if name in BANNED_CALLS:
                return f"{name}() is not allowed"
        if isinstance(node, ast.Attribute):
            if node.attr in BANNED_ATTRS:
                return f".{node.attr} is not allowed"
            if _is_dunder(node.attr):
                return f".{node.attr} is not allowed"
        elif isinstance(node, ast.Name) and _is_dunder(node.id):
            return f"{node.id} is not allowed"
    return None


def _norm(text: str) -> str:
    lines = text.replace("\r", "").split("\n")
    lines = [l.rstrip() for l in lines]
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines)


_NUMBER = re.compile(r"(-?\d+(?:\.\d+)?)")


def _numbers_equal(a: str, b: str) -> bool:
    x, y = float(a), float(b)
    return abs(x - y) <= 1e-6 * max(1.0, abs(x), abs(y))


def _lines_match(got: str, want: str) -> bool:
    if got == want:
        return True
    # Text must match exactly; numbers may differ in form (120 vs 120.0)
    # or by tiny float rounding (495.00000000000006 vs 495.0).
    g, w = _NUMBER.split(got), _NUMBER.split(want)
    if len(g) != len(w):
        return False
    for i, (a, b) in enumerate(zip(g, w)):
        if i % 2 == 0:
            if a != b:
                return False
        elif not _numbers_equal(a, b):
            return False
    return True


def outputs_match(got: str, want: str) -> bool:
    g, w = _norm(got).split("\n"), _norm(want).split("\n")
    return len(g) == len(w) and all(_lines_match(a, b) for a, b in zip(g, w))


def _pump(stream, buf, limit, on_overflow):
    try:
        while True:
            chunk = stream.read1(65536)
            if not chunk:
                break
            buf.extend(chunk)
            if len(buf) > limit:
                on_overflow()
                break
    except (OSError, ValueError):
        pass


def _feed(stream, data):
    try:
        stream.write(data)
    except (BrokenPipeError, OSError, ValueError):
        pass
    finally:
        try:
            stream.close()
        except OSError:
            pass


def _execute(code, stdin_text, timeout):
    env = {
        "PATH": os.environ.get("PATH", ""),
        "SYSTEMROOT": os.environ.get("SYSTEMROOT", ""),
        "TEMP": os.environ.get("TEMP", ""),
        "TMP": os.environ.get("TMP", ""),
        "PYTHONIOENCODING": "utf-8",
        "PYTHONHASHSEED": "0",
        "PYTHONDONTWRITEBYTECODE": "1",
    }
    cmd = [sys.executable, "-I", "-c", _LAUNCHER, code]

    with tempfile.TemporaryDirectory() as td:
        kwargs = {}
        if os.name == "nt":
            kwargs["creationflags"] = subprocess.CREATE_NO_WINDOW
        proc = subprocess.Popen(
            cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            cwd=td, env=env, **kwargs,
        )
        out, err = bytearray(), bytearray()
        overflow = threading.Event()

        def kill_overflow():
            overflow.set()
            proc.kill()

        threads = [
            threading.Thread(target=_feed, args=(proc.stdin, stdin_text.encode("utf-8")), daemon=True),
            threading.Thread(target=_pump, args=(proc.stdout, out, MAX_OUTPUT, kill_overflow), daemon=True),
            threading.Thread(target=_pump, args=(proc.stderr, err, MAX_OUTPUT, kill_overflow), daemon=True),
        ]
        for t in threads:
            t.start()
        timed_out = False
        try:
            proc.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
            proc.kill()
            proc.wait()
        for t in threads:
            t.join(timeout=2)
        for s in (proc.stdout, proc.stderr):
            s.close()

    if overflow.is_set():
        return {"status": "ok", "out": out[:MAX_OUTPUT].decode("utf-8", "replace"),
                "err": "Output limit exceeded: your program printed too much. Check for an endless loop.",
                "returncode": proc.returncode}
    if timed_out:
        return {"status": "timeout", "out": "", "err": ""}
    return {
        "status": "ok",
        "out": out.decode("utf-8", "replace"),
        "err": err.decode("utf-8", "replace"),
        "returncode": proc.returncode,
    }


def run_code(code: str, stdin_text: str, timeout: int = TIMEOUT_SECONDS):
    """Run code with stdin_text. Returns dict with status/out/err."""
    reason = check_code(code)
    if reason:
        return {"status": "blocked", "reason": reason, "out": "", "err": reason}
    if not _slots.acquire(timeout=SLOT_WAIT_SECONDS):
        return {"status": "busy", "out": "", "err": ""}
    try:
        return _execute(code, stdin_text, timeout)
    except Exception as e:  # noqa: BLE001
        return {"status": "error", "out": "", "err": str(e)}
    finally:
        _slots.release()


def judge(code: str, tests):
    """Run code against a list of TestCase-like objects.
    Returns (verdict, per_test_results, first_bad)."""
    results = []
    for t in tests:
        r = run_code(code, t.input_text)
        if r["status"] == "busy":
            return "busy", results, None
        if r["status"] == "blocked":
            results.append({"status": "blocked", "reason": r["reason"]})
            return "blocked", results, results[-1]
        if r["status"] == "timeout":
            results.append({"status": "timeout"})
            return "timeout", results, results[-1]
        if r["status"] != "ok" or r.get("returncode", 0) != 0:
            results.append({"status": "error", "err": r["err"], "out": r["out"]})
            return "error", results, results[-1]
        if outputs_match(r["out"], t.expected_output):
            results.append({"status": "pass"})
        else:
            results.append({
                "status": "wrong",
                "out": r["out"],
                "expected": t.expected_output,
            })
            return "wrong", results, results[-1]
    return "accepted", results, None
