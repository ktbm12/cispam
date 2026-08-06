from .base import *  # noqa: F403
from .base import env

DEBUG = True
SECRET_KEY = env(
    "DJANGO_SECRET_KEY",
    default="django-insecure-local-dev-only-key-do-not-use-in-production",
)
ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# A dev-only Ed25519 keypair so `manage.py runserver` works without any setup.
# Persisted to a gitignored file (not regenerated every restart) so a locally
# built desktop app's embedded public key keeps matching across dev sessions.
# Never used in production (LICENSE_SIGNING_PRIVATE_KEY_PEM must be set there).
if not LICENSE_SIGNING_PRIVATE_KEY_PEM:  # noqa: F405
    from licensing_protocol.keys import generate_keypair
    from licensing_protocol.keys import private_key_to_pem

    _dev_key_path = BASE_DIR / ".dev_signing_key.pem"  # noqa: F405
    if _dev_key_path.is_file():
        LICENSE_SIGNING_PRIVATE_KEY_PEM = _dev_key_path.read_text()
    else:
        _dev_private_key, _ = generate_keypair()
        LICENSE_SIGNING_PRIVATE_KEY_PEM = private_key_to_pem(_dev_private_key).decode("ascii")
        _dev_key_path.write_text(LICENSE_SIGNING_PRIVATE_KEY_PEM)
