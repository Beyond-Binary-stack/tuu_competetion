"""
Django settings for unity_contest project.

All deployment-specific values come from environment variables or a `.env`
file next to manage.py (see `.env.example`).
"""

import os
import secrets
from pathlib import Path

import environ

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env()
environ.Env.read_env(BASE_DIR / ".env")


def _load_secret_key():
    key = env("DJANGO_SECRET_KEY", default="")
    if key:
        return key
    # Persist an auto-generated key so sessions survive restarts.
    key_file = BASE_DIR / ".secret_key"
    if key_file.exists():
        return key_file.read_text().strip()
    key = secrets.token_urlsafe(50)
    key_file.write_text(key)
    return key


SECRET_KEY = _load_secret_key()

DEBUG = env.bool("DJANGO_DEBUG", default=False)

ALLOWED_HOSTS = env.list("DJANGO_ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

# Full origins incl. scheme, e.g. "http://10.0.0.5:8000,https://contest.example.com"
CSRF_TRUSTED_ORIGINS = env.list("DJANGO_CSRF_TRUSTED_ORIGINS", default=[
    "http://127.0.0.1:8000",
    "http://localhost:8000",
])

# Set to True only when the site is served over HTTPS (e.g. behind nginx with TLS).
USE_HTTPS = env.bool("DJANGO_USE_HTTPS", default=False)
if USE_HTTPS:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

LOGIN_URL = "login"

# Secret-ish path for the Django admin (default /admin/ is the first thing bots try)
ADMIN_PATH = env("DJANGO_ADMIN_PATH", default="psc-control/").strip("/") + "/"

SESSION_COOKIE_AGE = 60 * 60 * 12
SESSION_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "DENY"
SECURE_CONTENT_TYPE_NOSNIFF = True


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'unity_contest.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'unity_contest.wsgi.application'


# Database
# SQLite in WAL mode with a generous busy timeout handles many concurrent
# readers plus the occasional submission write without "database is locked".

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': env("DJANGO_DB_PATH", default=str(BASE_DIR / 'db.sqlite3')),
        'OPTIONS': {
            'timeout': 20,
            'transaction_mode': 'IMMEDIATE',
            'init_command': 'PRAGMA journal_mode=WAL; PRAGMA synchronous=NORMAL;',
        },
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}


PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
    "core.hashers.GroupPasswordHasher",
]


# Password validation
# https://docs.djangoproject.com/en/6.0/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/6.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = env("DJANGO_TIME_ZONE", default='Africa/Cairo')

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images) - served by WhiteNoise in production

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"
        if not DEBUG else "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}


# Logging: console + rotating file in logs/

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(exist_ok=True)
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "std": {"format": "%(asctime)s %(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {"class": "logging.StreamHandler", "formatter": "std"},
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(LOG_DIR / "contest.log"),
            "maxBytes": 5 * 1024 * 1024,
            "backupCount": 5,
            "formatter": "std",
            "encoding": "utf-8",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "INFO"},
    "loggers": {
        "django.request": {"handlers": ["console", "file"], "level": "WARNING", "propagate": False},
    },
}


# Contest runtime tuning
# Max number of student programs executing at the same time.
JUDGE_CONCURRENCY = env.int("JUDGE_CONCURRENCY", default=max(2, os.cpu_count() or 2))
# Minimum seconds between two submissions from the same group.
SUBMIT_COOLDOWN_SECONDS = env.int("SUBMIT_COOLDOWN_SECONDS", default=5)

# Unity University branding
SITE_NAME = 'The Unity University - Faculty of Computing and Information Technology'
