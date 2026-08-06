"""License token: canonical claims, signing, and verification.

Wire format: ``base64url(canonical_json_claims) + "." + base64url(signature)``.

This is deliberately not a full JWT: there is no header, no "alg" field, and
therefore no algorithm-confusion attack surface. The algorithm is always
Ed25519 and is implicit in which key material the caller supplies.
"""

from __future__ import annotations

import base64
import json
import time
import uuid
from dataclasses import asdict
from dataclasses import dataclass
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey

TOKEN_VERSION = 1

# Duration-type plan codes accepted in the `plan` claim.
PLAN_CODES = ("1m", "3m", "6m", "1y", "lifetime")

_REQUIRED_CLAIM_KEYS = (
    "license_key",
    "customer_id",
    "device_fingerprint_hash",
    "plan",
    "max_devices",
    "issued_at",
    "offline_grace_until",
    "jti",
)


class InvalidTokenError(Exception):
    """Raised for any malformed, unsigned, or signature-invalid token."""


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


@dataclass(frozen=True)
class LicenseClaims:
    """The signed claims embedded in a license token.

    ``device_fingerprint_hash`` is the single combined fingerprint hash used to
    bind a token to one machine. The 4 individual fuzzy-matching component
    hashes used for device-slot bookkeeping travel separately in the
    activate/validate HTTP payloads and are never part of the signed token.
    """

    license_key: str
    customer_id: str
    device_fingerprint_hash: str
    plan: str
    max_devices: int
    issued_at: int
    offline_grace_until: int
    jti: str
    expires_at: int | None = None
    version: int = TOKEN_VERSION

    def to_canonical_dict(self) -> dict[str, Any]:
        return asdict(self)

    def is_expired(self, *, now: int | None = None) -> bool:
        if self.expires_at is None:
            return False
        return (now if now is not None else int(time.time())) >= self.expires_at

    def is_within_offline_grace(self, *, now: int | None = None) -> bool:
        return (now if now is not None else int(time.time())) <= self.offline_grace_until


def new_jti() -> str:
    return uuid.uuid4().hex


def _canonical_bytes(claims: dict[str, Any]) -> bytes:
    return json.dumps(claims, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sign_token(claims: LicenseClaims, private_key: Ed25519PrivateKey) -> str:
    """Sign `claims` and return the compact wire-format token string."""
    payload = _canonical_bytes(claims.to_canonical_dict())
    signature = private_key.sign(payload)
    return f"{_b64url_encode(payload)}.{_b64url_encode(signature)}"


def verify_token(token: str, public_key: Ed25519PublicKey) -> LicenseClaims:
    """Verify `token`'s signature and shape, returning its claims.

    Raises `InvalidTokenError` for any structural or cryptographic failure.
    Does NOT check expiry/offline-grace — callers decide what to do with an
    expired-but-authentically-signed token (e.g. show "please renew" instead
    of treating it the same as a forged one).
    """
    try:
        encoded_payload, encoded_signature = token.split(".")
        payload = _b64url_decode(encoded_payload)
        signature = _b64url_decode(encoded_signature)
    except ValueError as exc:
        raise InvalidTokenError("malformed token") from exc

    try:
        public_key.verify(signature, payload)
    except InvalidSignature as exc:
        raise InvalidTokenError("signature verification failed") from exc

    try:
        raw = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise InvalidTokenError("malformed claims payload") from exc

    missing = [key for key in _REQUIRED_CLAIM_KEYS if key not in raw]
    if missing:
        raise InvalidTokenError(f"missing claims: {', '.join(missing)}")

    return LicenseClaims(
        license_key=raw["license_key"],
        customer_id=raw["customer_id"],
        device_fingerprint_hash=raw["device_fingerprint_hash"],
        plan=raw["plan"],
        max_devices=raw["max_devices"],
        issued_at=raw["issued_at"],
        offline_grace_until=raw["offline_grace_until"],
        jti=raw["jti"],
        expires_at=raw.get("expires_at"),
        version=raw.get("version", TOKEN_VERSION),
    )
