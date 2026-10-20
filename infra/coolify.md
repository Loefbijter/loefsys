# Coolify

Staging and production run as two Coolify applications on one server. GitHub Actions
builds the image and pushes it to GHCR, then calls the application's Coolify deploy
webhook (`.github/workflows/deploy-staging.yml` and `deploy-production.yml`).

| | Staging | Production |
|---|---|---|
| Deploys | every push to `main` | every published GitHub release |
| Image | `ghcr.io/loefbijter/loefsys:staging` | `ghcr.io/loefbijter/loefsys:production` |
| Domain | `https://staging.loefbijter.nl` | `https://app.loefbijter.nl` |
| Database | its own Coolify Postgres, invented data only | its own Coolify Postgres |
| Post-deployment command | `python manage.py reset_staging` | `python manage.py migrate --no-input` |

Coolify runs its pre-deployment command in the *old* container, so migrations go in the
post-deployment command, which runs in the new one.

## Application settings

Both are "Docker Image" applications with port `8000` exposed and a persistent storage
volume mounted at `/app/media`. Coolify's proxy (Traefik) terminates HTTPS with a
Let's Encrypt certificate and sets `X-Forwarded-Proto`.

Environment variables, on top of the database URL from the Coolify Postgres resource
(`DJANGO_DATABASE_URL`, its internal URL):

```
DJANGO_SECRET_KEY=            # different on each
DJANGO_DEBUG=false
DJANGO_ALLOWED_HOSTS=staging.loefbijter.nl
DJANGO_CSRF_TRUSTED_ORIGINS=https://staging.loefbijter.nl
DJANGO_SECURE_SSL_REDIRECT=true
```

Staging only:

```
LOEFSYS_ALLOW_RESET=true
LOEFSYS_STAGING_PASSWORD=     # password for every invented user
DJANGO_EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
```

Never set `LOEFSYS_ALLOW_RESET` on production: `reset_staging` drops every table.

## Resetting staging

Every deploy to staging wipes its database and fills it with invented members, groups,
boats, events and reservations. To reset it by hand, either press **Redeploy** on the
staging application, or open its **Terminal** in Coolify and run:

```
python manage.py reset_staging
```

Log in as `admin@example.org` (superuser) or `lid1@example.org` to `lid28@example.org`,
all with `LOEFSYS_STAGING_PASSWORD`.

## Deploy webhooks

Each GitHub environment (`staging`, `production`) has two secrets:

- `COOLIFY_WEBHOOK_URL`: the application's deploy webhook, from its **Webhooks** tab
  (`https://<coolify>/api/v1/deploy?uuid=<uuid>&force=false`).
- `COOLIFY_TOKEN`: a Coolify API token with the `deploy` permission (**Keys & Tokens**).

## Backups

The production Postgres resource has a daily scheduled backup in Coolify. Staging has
none, since its data is invented and rebuilt on every deploy.
