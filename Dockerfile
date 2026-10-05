# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.9 AS uv

FROM python:3.13-slim AS builder
COPY --from=uv /uv /uvx /usr/local/bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

# GNU gettext, for compilemessages below. Only in the builder stage.
RUN apt-get update \
    && apt-get install -y --no-install-recommends gettext \
    && rm -rf /var/lib/apt/lists/*

# Dependency layer, cached independently of app source changes.
COPY pyproject.toml uv.lock ./
RUN uv sync --locked --no-dev --no-install-project

# App source.
COPY . .
RUN uv sync --locked --no-dev

# Build-time-only dummy config so management commands can import settings
# without real secrets/a real database. Never present in the runtime stage.
ENV DJANGO_SECRET_KEY=build-time-unused \
    DJANGO_DATABASE_URL=sqlite://:memory: \
    DJANGO_DEBUG=false \
    DJANGO_STATIC_MANIFEST=true

RUN uv run manage.py tailwind --minify
RUN uv run manage.py collectstatic --no-input
# The .mo files are not in git; build them from the .po catalogues.
RUN uv run manage.py compilemessages

FROM python:3.13-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    DJANGO_STATIC_MANIFEST=true
RUN groupadd -r loefsys && useradd -r -g loefsys loefsys
WORKDIR /app
COPY --from=builder --chown=loefsys:loefsys /app /app
# WORKDIR creates /app as root before the COPY above runs, and --chown only
# applies to what COPY creates under it, not the pre-existing directory itself.
# Without this, Django can't write into /app (a bind/sqlite fallback file) or
# /app/media (user-uploaded files) at runtime.
RUN chown loefsys:loefsys /app
USER loefsys
EXPOSE 8000
# The healthcheck talks to gunicorn directly, so it sends what Apache would: a
# host from DJANGO_ALLOWED_HOSTS and X-Forwarded-Proto, so that neither the host
# check nor the HTTPS redirect rejects it.
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
    CMD ["python", "/app/infra/scripts/healthcheck.py"]
CMD ["gunicorn", "loefsys.wsgi:application", "--bind", "0.0.0.0:8000", \
     "--workers", "3", "--timeout", "60", \
     "--access-logfile", "-", "--error-logfile", "-"]
