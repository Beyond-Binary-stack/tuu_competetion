"""Production server for the contest (works on Windows and Linux).

    python serve.py                 # 0.0.0.0:8000
    python serve.py --port 80
"""
import argparse
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "unity_contest.settings")

from waitress import serve  # noqa: E402

from unity_contest.wsgi import application  # noqa: E402


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8000")))
    parser.add_argument("--threads", type=int, default=int(os.environ.get("THREADS", "32")))
    args = parser.parse_args()
    proxy = {}
    if os.environ.get("TRUSTED_PROXY"):
        proxy = {
            "trusted_proxy": os.environ["TRUSTED_PROXY"],
            "trusted_proxy_headers": {"x-forwarded-for", "x-forwarded-proto", "x-forwarded-host"},
        }
    print(f"Serving contest on http://{args.host}:{args.port} with {args.threads} threads")
    serve(
        application,
        host=args.host,
        port=args.port,
        threads=args.threads,
        connection_limit=500,
        channel_timeout=60,
        **proxy,
    )


if __name__ == "__main__":
    main()
