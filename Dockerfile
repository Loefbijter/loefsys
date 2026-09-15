# syntax=docker/dockerfile:1

FROM ghcr.io/astral-sh/uv:0.9 AS uv

FROM python:3.12-slim AS builder
COPY --from=uv /uv /uvx /usr/local/bin/
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONDONTWRITEBYTECODE=1
WORKDIR /app

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
    DJANGO_DEBUG=false

RUN uv run manage.py tailwind --minify
RUN uv run manage.py collectstatic --no-input

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"
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
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/')" || exit 1
CMD ["gunicorn", "loefsys.wsgi:application", "--bind", "0.0.0.0:8000", \
     "--workers", "3", "--timeout", "60", \
     "--access-logfile", "-", "--error-logfile", "-"]
