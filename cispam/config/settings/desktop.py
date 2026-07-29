import os
from pathlib import Path
from .base import *  # noqa
from .base import env

# GENERAL
DEBUG = False
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]

# DESKTOP DATA PATH
# Store persistent data in the user's home directory (AppData on Windows)
if os.name == 'nt':
    app_data = os.environ.get('APPDATA', str(Path.home()))
    DATA_DIR = Path(app_data) / "cispam"
else:
    DATA_DIR = Path.home() / ".cispam"

DATA_DIR.mkdir(parents=True, exist_ok=True)

# DATABASES
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATA_DIR / "db.sqlite3",
        "ATOMIC_REQUESTS": True,
    }
}

# MEDIA
MEDIA_ROOT = str(DATA_DIR / "media")
MEDIA_URL = "/media/"

# STATIC
# WhiteNoise is used to serve static files in production WSGI
INSTALLED_APPS = ["whitenoise.runserver_nostatic"] + [app for app in INSTALLED_APPS if app != "whitenoise.runserver_nostatic"]
STATIC_ROOT = str(BASE_DIR / "staticfiles")

# EMAIL
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
