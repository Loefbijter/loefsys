Deployment
==========
Loefsys is packaged as a Docker image and deployed via ``docker compose`` on two long-lived hosts: staging and production. Both are existing servers reached over SSH -- this pipeline does not provision infrastructure.

Overview
--------
* Pushing to ``main`` builds the image, pushes it to GHCR (GitHub Container Registry), and deploys it to staging automatically (``.github/workflows/deploy-staging.yml``).
* Publishing a GitHub Release does the same for production (``.github/workflows/deploy-production.yml``), gated behind a required-reviewer approval on the ``production`` GitHub Environment.
* Both workflows take a database backup and run migrations before recreating the ``web`` container. Neither workflow provisions a host, installs Docker, or creates a database from scratch -- see `Pre-flight checklist`_.

.. _pre-flight-checklist:

Pre-flight checklist
---------------------
Do this once, in order, on each host, before the deploy workflows are wired up (before creating the GitHub Environments/secrets described below). This is manual and deliberately not automated: it involves the *existing* production database, and getting it wrong is not something CI should be trusted to do unattended.

#. SSH into the host. Identify how the current Django process runs today (systemd unit, supervisor, something ad hoc?) and find the Apache vhost config that proxies to it.

#. Locate the database: engine, host/port, database name/user, and whether it's reachable from a Docker bridge network on that host. This decides which variant of ``docker-compose.yml`` applies -- see the comment at the top of that file.

#. **Take a full backup immediately**, before anything else touches the host: ``pg_dump -Fc`` (or a plain file copy, if it turns out to still be SQLite). Copy it off-host.

#. Locate current media storage (``MEDIA_ROOT``). If member-uploaded files exist on disk, note the path -- they need a one-time copy into the new ``media_data`` volume so redeploys don't silently discard them.

#. Run ``manage.py showmigrations`` against the real database, read-only, and compare against ``main``'s migration files. Reconcile every mismatch manually (typically ``migrate --fake`` for migrations that already reflect reality) *before* letting any workflow run ``migrate`` unattended. Treat this as its own task, not a rubber stamp -- migrations were only recently properly committed to git, so mismatches are expected.

#. Confirm the hostname each environment should answer on (production: ``app.loefbijter.nl``, confirm this is still accurate; staging: confirm/pick one), for ``DJANGO_ALLOWED_HOSTS``/``DJANGO_CSRF_TRUSTED_ORIGINS``.

#. Confirm the staging host -- same VPS as production (different port/compose project directory) or a separate machine. Either works; it only affects the ``staging`` Environment's ``SSH_HOST`` secret.

#. Confirm ``docker`` and the ``docker compose`` v2 plugin are installed on both hosts (install manually once if not).

#. Create the real ``.env`` on each host from ``infra/.env.production.example`` / ``infra/.env.staging.example``, then ``chmod 600`` it.

#. Only after all of the above: create the ``staging`` and ``production`` GitHub Environments (repo Settings → Environments), each with their own ``SSH_HOST``, ``SSH_USER``, ``SSH_KEY`` secrets, add a required-reviewers rule to ``production``, then merge the two deploy workflow files.

GHCR images are public (matching the public GitHub repo), so neither host needs registry credentials to ``docker compose pull``.

Reverse proxy
-------------
No Apache config lives in this repository -- there's nothing to template or automate. As a one-time manual step, point the existing vhost's proxy directive at ``127.0.0.1:8000`` (matching the port mapping in ``docker-compose.yml``), keeping its current TLS-termination and ``X-Forwarded-Proto`` behaviour, which ``SecuritySettings.SECURE_PROXY_SSL_HEADER`` already expects.

Rollback
--------
GHCR keeps every tagged image. Rolling back does not need a rebuild -- on the host, in the compose project directory::

    $ IMAGE_TAG=<previous-good-tag> docker compose up -d

If the bad release also shipped a migration, reverting it is a **separate, manual** step (``manage.py migrate <app> <previous_migration>``) -- deliberately not automated, for the same reason unattended ``migrate`` isn't allowed until the pre-flight checklist's migration-reconciliation step is done.

See also
--------
``infra/README.md`` covers the same material from the perspective of someone already SSHed into a host, without needing to go read this page.
