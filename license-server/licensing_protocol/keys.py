"""Ed25519 keypair generation and PEM (de)serialization for license signing.

Run ``py -m licensing_protocol.keys`` to generate a fresh keypair for a new
deployment.

- The PRIVATE key stays on the license server only (env var / secret manager
  — e.g. ``LICENSE_SIGNING_PRIVATE_KEY_PEM`` — never committed to git).
- The PUBLIC key is embedded, at build time, into the desktop app's compiled
  licensing core. It is not a secret: anyone can use it to verify a token was
  issued by the real server, but that alone doesn't let them forge one.
"""

from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey


def generate_keypair() -> tuple[Ed25519PrivateKey, Ed25519PublicKey]:
    private_key = Ed25519PrivateKey.generate()
    return private_key, private_key.public_key()


def private_key_to_pem(private_key: Ed25519PrivateKey) -> bytes:
    return private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )


def public_key_to_pem(public_key: Ed25519PublicKey) -> bytes:
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )


def load_private_key_from_pem(pem_data: bytes) -> Ed25519PrivateKey:
    key = serialization.load_pem_private_key(pem_data, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError("PEM data is not an Ed25519 private key")
    return key


def load_public_key_from_pem(pem_data: bytes) -> Ed25519PublicKey:
    key = serialization.load_pem_public_key(pem_data)
    if not isinstance(key, Ed25519PublicKey):
        raise TypeError("PEM data is not an Ed25519 public key")
    return key


def _main() -> None:
    private_key, public_key = generate_keypair()
    print("=== CISPAM license signing keypair (Ed25519) ===\n")
    print("PRIVATE KEY — server secret, e.g. LICENSE_SIGNING_PRIVATE_KEY_PEM.")
    print("Never commit this to git.\n")
    print(private_key_to_pem(private_key).decode("ascii"))
    print("PUBLIC KEY — embed into the desktop app's licensing core at build time.\n")
    print(public_key_to_pem(public_key).decode("ascii"))


if __name__ == "__main__":
    _main()
