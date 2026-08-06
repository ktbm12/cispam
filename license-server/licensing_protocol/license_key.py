"""CISPAM license key format: ``CISP-XXXXX-XXXXX-XXXXX-XXXXX``.

20 Crockford-base32 characters encode a random value, grouped into four
human-friendly blocks of 5. The last character is a checksum computed over
the preceding characters, so the desktop activation form can catch typos
(mistyped/transposed characters) before making a network call.

The checksum is NOT a security control — it only rejects malformed input
early. Whether a key was ever actually issued, and its current status, is
always decided server-side.
"""

from __future__ import annotations

import secrets

# Crockford base32: excludes I, L, O, U to avoid visual ambiguity/accidental words.
_ALPHABET = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
_GROUP_SIZE = 5
_NUM_GROUPS = 4
_PREFIX = "CISP"


def _checksum_char(data_chars: str) -> str:
    """Positional-weighted mod-32 checksum over the alphabet."""
    total = sum((i + 1) * _ALPHABET.index(c) for i, c in enumerate(data_chars))
    return _ALPHABET[total % len(_ALPHABET)]


def generate_license_key() -> str:
    """Generate a new, randomly-keyed license key string.

    Format only — the caller is responsible for persisting it as an actual
    `License` row before it means anything.
    """
    body_len = _GROUP_SIZE * _NUM_GROUPS - 1  # last char of the key is the checksum
    body = "".join(secrets.choice(_ALPHABET) for _ in range(body_len))
    key = f"{body}{_checksum_char(body)}"
    groups = [key[i : i + _GROUP_SIZE] for i in range(0, len(key), _GROUP_SIZE)]
    return f"{_PREFIX}-{'-'.join(groups)}"


def normalize_license_key(raw: str) -> str:
    """Uppercase and strip whitespace/hyphens for lenient user input."""
    return raw.strip().upper().replace(" ", "").replace("-", "")


def is_well_formed(raw: str) -> bool:
    """Cheap, fully offline structural + checksum check.

    True does not mean the key was ever issued — only that it is shaped like
    one and worth sending to the server. False means it is definitely not a
    valid key (e.g. a typo), so the UI can reject it before any network call.
    """
    normalized = normalize_license_key(raw)
    if normalized.startswith(_PREFIX):
        normalized = normalized[len(_PREFIX) :]
    if len(normalized) != _GROUP_SIZE * _NUM_GROUPS:
        return False
    if any(char not in _ALPHABET for char in normalized):
        return False
    body, checksum = normalized[:-1], normalized[-1]
    return _checksum_char(body) == checksum
