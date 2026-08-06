"""
Canonical license-token contract shared between the CISPAM license server
(which signs tokens) and the CISPAM desktop client (which only ever verifies
them). See ../../docs/LICENSE_TOKEN_FORMAT.md for the wire-format spec.

This package is intentionally dependency-light (only `cryptography`) so the
exact same source file can be vendored, byte-for-byte, into the desktop app's
`cispam.licensing` package and Cython-compiled there. Do not add Django or any
other server-only dependency here — that would make it unusable on the
desktop side and force the two implementations to drift apart.
"""
