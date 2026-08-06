FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim AS python

FROM python AS python-build-stage

ARG APP_HOME=/app
WORKDIR ${APP_HOME}

ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=0

RUN apt-get update && apt-get install --no-install-recommends -y \
  build-essential \
  libpq-dev \
  wait-for-it

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --no-install-project

COPY . ${APP_HOME}

RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync

ENV PATH="/${APP_HOME}/.venv/bin:$PATH"

COPY ./compose/production/django/entrypoint /entrypoint
RUN sed -i 's/\r$//g' /entrypoint && chmod +x /entrypoint

COPY ./compose/local/django/start /start
RUN sed -i 's/\r$//g' /start && chmod +x /start

ENTRYPOINT ["/entrypoint"]
