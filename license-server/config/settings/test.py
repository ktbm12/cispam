from .base import *  # noqa: F403
from .base import env

SECRET_KEY = "django-insecure-test-key-not-for-production"
DEBUG = False
ALLOWED_HOSTS = ["testserver", "localhost", "127.0.0.1"]
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]  # fast tests
EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# Deterministic Ed25519 keypair for tests — generated once and pinned so test
# fixtures (expected public key, expected signatures) don't change between runs.
LICENSE_SIGNING_PRIVATE_KEY_PEM = env(
    "LICENSE_SIGNING_PRIVATE_KEY_PEM",
    default="""-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIOnbIyubXFXChmVOWyE9EU2CDsOX+2vBPeGa4vc/dHIt
-----END PRIVATE KEY-----
""",
)
