"""Login throttling and online-device tracking (in-process cache; single server process)."""
import hashlib
import time

from django.core.cache import cache

# A wrong password for the same name from the same device
PAIR_MAX_FAILS, PAIR_LOCK_SECONDS = 5, 5 * 60
# Many wrong attempts from one IP (whole venue may share one IP, so keep it generous)
IP_MAX_FAILS, IP_LOCK_SECONDS = 30, 10 * 60
FAIL_WINDOW_SECONDS = 10 * 60
DEVICE_ONLINE_SECONDS = 120


def client_ip(request):
    return request.META.get("REMOTE_ADDR", "")


def _keys(ip, username):
    name = hashlib.sha256(username.strip().lower().encode()).hexdigest()[:16]
    ip = ip.replace(":", "_")
    return (f"lf:pair:{ip}:{name}", f"lk:pair:{ip}:{name}", PAIR_MAX_FAILS, PAIR_LOCK_SECONDS), \
           (f"lf:ip:{ip}", f"lk:ip:{ip}", IP_MAX_FAILS, IP_LOCK_SECONDS)


def login_locked_seconds(ip, username):
    """Seconds left on an active lock, or 0."""
    now = time.time()
    left = [cache.get(lock_key, 0) - now for _, lock_key, _, _ in _keys(ip, username)]
    return max(0, int(max(left)))


def register_login_failure(ip, username):
    for fail_key, lock_key, max_fails, lock_seconds in _keys(ip, username):
        cache.add(fail_key, 0, FAIL_WINDOW_SECONDS)
        try:
            n = cache.incr(fail_key)
        except ValueError:
            cache.set(fail_key, 1, FAIL_WINDOW_SECONDS)
            n = 1
        if n >= max_fails:
            cache.set(lock_key, time.time() + lock_seconds, lock_seconds)
            cache.delete(fail_key)


def clear_login_failures(ip, username):
    pair_fail, pair_lock = _keys(ip, username)[0][:2]
    cache.delete_many([pair_fail, pair_lock])


def touch_device(group_id, session_key, ip):
    if not session_key:
        return
    key = f"devices:{group_id}"
    now = time.time()
    devices = cache.get(key) or {}
    last = devices.get(session_key)
    if last and now - last[0] < 15:
        return
    devices = {k: v for k, v in devices.items() if now - v[0] < DEVICE_ONLINE_SECONDS}
    devices[session_key] = (now, ip)
    cache.set(key, devices, DEVICE_ONLINE_SECONDS * 5)


def online_devices(group_id):
    """List of IPs of devices seen in the last couple of minutes."""
    now = time.time()
    devices = cache.get(f"devices:{group_id}") or {}
    return [ip for ts, ip in devices.values() if now - ts < DEVICE_ONLINE_SECONDS]


def forget_devices(group_id):
    cache.delete(f"devices:{group_id}")
