# CISPAM License Token — Wire Format Spec

This document is the single source of truth for the license token format. Both
sides implement it from the **same source file**
(`license-server/licensing_protocol/tokens.py`), which is vendored byte-for-byte
into the desktop app at `cispam/cispam/licensing/protocol/tokens.py` (see Phase 4).
Do not hand-reimplement this logic on either side — copy the file forward so the
two verifiers can never drift apart.

## Why not a standard JWT?

JWT allows the token itself to declare its signing algorithm (the `alg` header),
which is the root cause of real-world "algorithm confusion" attacks (e.g. a
server configured to accept both RS256 and HS256 can be tricked into verifying
an attacker-forged HS256 token using the *public* RSA key as an HMAC secret).
CISPAM tokens are always Ed25519, chosen out-of-band by which key the verifier
was given — there is no `alg` field for an attacker to manipulate.

## Wire format

```
<base64url(canonical_json_claims)> "." <base64url(ed25519_signature)>
```

- `canonical_json_claims` = `json.dumps(claims, sort_keys=True, separators=(",", ":"))`
  encoded as UTF-8. Deterministic key ordering and no whitespace so the exact
  same bytes are signed and verified.
- `ed25519_signature` = `Ed25519PrivateKey.sign(canonical_json_claims_bytes)`.
- Both parts are base64url-encoded with padding stripped (`=` removed).

## Claims

| Field | Type | Meaning |
|---|---|---|
| `license_key` | string | The formatted license key this token was issued for. |
| `customer_id` | string | Server-side customer identifier (UUID). |
| `device_fingerprint_hash` | string | Single combined hash binding this token to one machine. |
| `plan` | string | One of `1m`, `3m`, `6m`, `1y`, `lifetime`. |
| `max_devices` | int | Device-slot limit at time of issuance (informational; slot enforcement is server-side). |
| `issued_at` | int | Unix timestamp when the server issued this token. |
| `expires_at` | int \| null | Unix timestamp the license itself expires; `null` for `lifetime`. |
| `offline_grace_until` | int | Unix timestamp until which the app may run fully offline before requiring a fresh online validate. |
| `jti` | string | Random nonce, unique per issuance (`uuid4().hex`). |
| `version` | int | Token schema version, currently `1`. |

Note: the 4 individual fuzzy-matching fingerprint component hashes (Machine
GUID, volume serial, CPU id, motherboard UUID — see §3 of the architecture
plan) are **not** part of the signed token. They travel only in the
activate/validate HTTP request/response bodies and live server-side on the
`Device` row, used purely for fuzzy device-slot bookkeeping. The token only
carries the single combined hash used for the fast local "is this my machine"
check.

## What verification does and does not check

`verify_token()` checks the signature and that all required claims are
present. It deliberately does **not** check `expires_at` or
`offline_grace_until` — callers must check those themselves against the
current time (reconciled with the anti-rollback clock anchor, see §4/§5 of the
architecture plan), so an expired-but-authentically-signed token can be told
apart from a forged one and shown a different message ("please renew" vs.
"invalid license").

## Key handling

- Server holds the Ed25519 **private** key (`LICENSE_SIGNING_PRIVATE_KEY_PEM`
  env var), generated via `py -m licensing_protocol.keys`.
- Desktop app embeds only the **public** key, baked in at build time (see
  Phase 5 of the architecture plan). The public key is not secret — anyone can
  verify a genuine token with it — but it cannot be used to sign new ones.
