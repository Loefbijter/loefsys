# infra/

Operational reference for whoever is SSHed into a staging/production host — the full pipeline writeup lives in `docs/deployment.rst` (Sphinx), this is the short version for reading directly on the box.

## `.env`

Each host has its own `.env` in the compose project directory (e.g. `/opt/loefsys/.env`), created once by hand from `.env.production.example` or `.env.staging.example`. It is **never committed** — `docker-compose.yml` reads it via `env_file:`.

```
chmod 600 .env
```

so only the deploy user can read it.

## `docker-compose.yml`

Deploys only ever run:

```
docker compose pull
docker compose run --rm web python manage.py migrate --no-input
docker compose up -d
```

**Never** run `docker compose down -v` or `--volumes` — that destroys the `db_data`/`media_data` named volumes. Plain `docker compose down` (no `-v`) still isn't used by the deploy pipeline at all; it only ever pulls and recreates via `up -d`.

The file assumes Postgres is containerized alongside the app (a `db` service in the same compose file). If your host runs Postgres natively instead, see the comment at the top of `docker-compose.yml` for the swap.

## Backups

`scripts/backup-db.sh` takes a `pg_dump`, gzips it into `backups/`, and prunes anything beyond the last 14. Both deploy workflows run it automatically immediately before `migrate`. To run it by hand:

```
cd /opt/loefsys
./infra/scripts/backup-db.sh
```

To restore one:

```
gunzip -c backups/loefsys-<timestamp>.sql.gz | docker compose exec -T db psql -U "$POSTGRES_USER" "$POSTGRES_DB"
```

## Rollback

No rebuild needed — the compose file's image tag is parametrized:

```
IMAGE_TAG=<previous-good-tag> docker compose up -d
```

Find previous tags on the [GHCR package page](https://github.com/Loefbijter/loefsys/pkgs/container/loefsys) or `git tag`/GitHub Releases for production. A migration shipped by a bad release is **not** auto-reverted — that's a separate, manual `manage.py migrate <app> <previous_migration>` if it's ever actually needed.
