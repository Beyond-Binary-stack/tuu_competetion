# PSC Python Contest (Django)

## Commands
- Install: `pip install -r requirements.txt`
- Tests: `python manage.py test core` (~40s; runs real student-code subprocesses)
- Production server: `python manage.py collectstatic --noinput` then `python serve.py --port 8000` (waitress, Windows + Linux)
- Dev server: set `DJANGO_DEBUG=True` then `python manage.py runserver`
- Seed problems/tests (safe to re-run; never duplicates groups): `python manage.py seed`
- Live DB backup (safe while running): `python manage.py backup_db` -> `backups/`

## Config
- All deployment settings come from env vars / `.env` (see `.env.example`).
- DEBUG defaults to False; ALLOWED_HOSTS / CSRF_TRUSTED_ORIGINS must include the server IP/domain.
- Run a single `serve.py` process (judge concurrency semaphore and stats cache are in-process).

## Security (core/security.py)
- Login lockout: 5 wrong tries per (IP, name) -> 5 min; 30 wrong tries per IP -> 10 min. Relies on correct REMOTE_ADDR
  (behind nginx set TRUSTED_PROXY, otherwise every client looks like 127.0.0.1).
- `Group.session_version` bump logs out all devices of a group (password change / "Log out all devices").
- Django admin lives at `DJANGO_ADMIN_PATH` (default `psc-control/`); its login goes through the rate-limited `/login/`.

## Notes
- Group passwords use the lighter `core.hashers.GroupPasswordHasher`; old hashes upgrade on login.
- Student code runner: `core/runner.py` (AST blocklist, 3s timeout, 20KB output cap, rlimits on POSIX).
- Judge rules: `input("prompt")` prompts are NOT printed (students learn to write prompts); output lines must match
  exactly except numbers compare by value (`120` == `120.0`, tiny float error ignored). See `outputs_match`.
- Problems: students are beginners (course book chapters 1-2 up to the `for` loop: no `//`, no `:.2f`, no lists).
  Source of truth is `PROBLEMS` in `core/management/commands/seed.py`; `seed` deletes problems not in the list.
