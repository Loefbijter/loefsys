#!/usr/bin/env bash
# Takes a full backup of the Postgres database before a deploy touches it.
#
# Written for the "containerized db" compose variant (a `db` service defined in
# docker-compose.yml). If the pre-flight investigation in docs/deployment.rst
# instead found Postgres already running natively on the host, replace the
# `docker compose exec` line below with a throwaway-container dump against
# DATABASE_URL instead, e.g.:
#   docker run --rm --network host --env-file .env postgres:16 \
#     bash -c 'pg_dump "$DJANGO_DATABASE_URL"' | gzip > "$OUT"
set -euo pipefail
cd "$(dirname "$0")/../.."

RETENTION_COUNT=14
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
OUT="backups/loefsys-${STAMP}.sql.gz"

mkdir -p backups
# shellcheck disable=SC2016  # single quotes are intentional: $POSTGRES_* expand inside the container
docker compose exec -T db bash -c 'pg_dump -U "$POSTGRES_USER" "$POSTGRES_DB"' | gzip > "$OUT"

echo "Backup written to ${OUT}"

# Keep only the most recent RETENTION_COUNT backups.
# shellcheck disable=SC2012
ls -1t backups/loefsys-*.sql.gz 2>/dev/null | tail -n "+$((RETENTION_COUNT + 1))" | xargs -r rm --
