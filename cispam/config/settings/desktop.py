import os
from pathlib import Path
from .base import *  # noqa
from .base import env, INSTALLED_APPS

# =============================================================================
# SECURITY
# =============================================================================
# A unique secret key for the desktop installation.
# This is safe to hardcode because the desktop app runs locally only (127.0.0.1).
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="cispam-desktop-local-only-key-xn7HlVwKROgOxOe5GxpHQhVrxvH28j8bHGxs7CI93zDg",
)

# GENERAL
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# =============================================================================
# DESKTOP DATA PATH
# =============================================================================
# Store persistent data in the user's home directory (AppData on Windows)
if os.name == 'nt':
    app_data = os.environ.get('APPDATA', str(Path.home()))
    DATA_DIR = Path(app_data) / "cispam"
else:
    DATA_DIR = Path.home() / ".cispam"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# =============================================================================
# DATABASES — SQLite for desktop (no PostgreSQL needed)
# =============================================================================
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db.sqlite3",
        "ATOMIC_REQUESTS": True,
    }
}

# =============================================================================
# MEDIA
# =============================================================================
MEDIA_ROOT = str(DATA_DIR / "media")
MEDIA_URL = "/media/"

# =============================================================================
# STATIC — WhiteNoise serves static files from the bundled exe
# =============================================================================
INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + [app for app in INSTALLED_APPS if app != "whitenoise.runserver_nostatic"]
STATIC_ROOT = str(BASE_DIR / "staticfiles")

# =============================================================================
# EMAIL — Console backend (no SMTP server needed on desktop)
# =============================================================================
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# REDIS / CELERY — Disabled for desktop (no Redis server available)
# =============================================================================
# Override base.py Redis/Celery settings since there's no Redis on a desktop machine
REDIS_URL = ""
REDIS_SSL = False
CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = "cache+memory://"
CELERY_BROKER_USE_SSL = None
CELERY_REDIS_BACKEND_USE_SSL = None
CELERY_TASK_ALWAYS_EAGER = True  # Execute tasks synchronously (no worker needed)
CELERY_TASK_EAGER_PROPAGATES = True

# =============================================================================
# CACHES — Local memory cache (no Redis needed)
# =============================================================================
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
    }
}
