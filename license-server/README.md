# CISPAM License Server

Activation/validation API + admin dashboard for CISPAM desktop licenses. See
`../docs/LICENSE_TOKEN_FORMAT.md` for the token spec this service signs, and
the approved architecture plan for the full design/rationale.

Status: **Phase 1 (project skeleton + crypto/token contracts) only.** The
`licenses` app has no models/API/dashboard yet — that's Phase 2/3.

## Local development

Requires [uv](https://docs.astral.sh/uv/). No Python version manager needed
beyond what `uv` installs (`requires-python = ">=3.12"`).

```
cd license-server
uv sync
uv run manage.py migrate
uv run manage.py createsuperuser
uv run manage.py runserver
```

The first run auto-generates a dev-only Ed25519 signing keypair and persists
it to `.dev_signing_key.pem` (gitignored) so it stays stable across restarts —
see `config/settings/local.py`. Never use this key in production.

### Or via Docker Compose

```
docker compose -f docker-compose.local.yml up --build
```

Serves on `http://localhost:8100/`.

## Generating a production signing keypair

```
uv run python -m licensing_protocol.keys
```

- Put the **private** key PEM in the production env as
  `LICENSE_SIGNING_PRIVATE_KEY_PEM` (see `.envs/.production/.django`, not
  committed — create it locally following the shape of `.envs/.local/.django`).
- Embed the **public** key into the desktop app's compiled licensing core at
  build time (Phase 5 — see `cispam/.github/workflows/build-windows.yml`).

Rotating this key invalidates every previously issued token still relying on
offline grace — treat it as a rare, coordinated operation, not routine
maintenance.

## Production deployment

```
docker compose -f docker-compose.production.yml up --build -d
```

Before deploying:
- Create `.envs/.production/.django` and `.envs/.production/.postgres`
  (gitignored — not present in this repo) with at least: `DJANGO_SECRET_KEY`,
  `DJANGO_ALLOWED_HOSTS`, `DJANGO_ADMIN_URL`, `LICENSE_SIGNING_PRIVATE_KEY_PEM`,
  `REDIS_URL=redis://redis:6379/0`, and the Postgres credentials.
- Edit `compose/production/traefik/traefik.yml`: replace the placeholder
  domain (`license.cispam.org`) and ACME contact email with real values.
- This stack runs its own Traefik instance on ports 80/443. If you're hosting
  this on the same VPS as the main CISPAM production stack, you cannot run
  two services both binding those ports — either put this service on a
  separate host, or (better, as a follow-up) consolidate onto one shared
  Traefik instance with a second router rule instead of running two.

## Project layout

- `licensing_protocol/` — dependency-light (only `cryptography`) token
  signing/verification and license-key formatting. This exact source is
  vendored into the desktop app (`cispam/cispam/licensing/protocol/`) so both
  sides implement the wire format identically — see the module docstrings and
  `../docs/LICENSE_TOKEN_FORMAT.md`.
- `licenses/` — Django app: models, REST API, business logic (Phase 2).
- `dashboard/` — staff-only Tailwind admin UI (Phase 3, not yet created).
- `config/` — Django settings (`base`/`local`/`production`/`test`), following
  the same split used by `cispam/config/settings/`.
