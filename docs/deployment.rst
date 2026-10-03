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

Moving an existing database into the Docker setup
-------------------------------------------------

Production currently runs the code from the ``feat/production-settings`` branch. Its migration files are identical to ``main``'s, so an existing production database can be copied straight into the new ``db`` container and migrated to the current code in one step. Do this in a quiet moment, because writes to the old site after the dump are lost.

#. Stop the old Django process (or put it in maintenance), so nothing writes to the old database any more.

#. Dump the old database in Postgres' custom format, and copy the dump off-host too::

    $ pg_dump -Fc --no-owner --no-acl -h <old-host> -U <old-user> <old-db> > loefsys-before-docker.dump

#. On the host, in the compose project directory, start only the database. It creates an empty ``loefsys`` database from ``POSTGRES_*`` in ``.env``::

    $ docker compose up -d db

#. Load the dump into it::

    $ docker compose exec -T db sh -c 'pg_restore -U "$POSTGRES_USER" -d "$POSTGRES_DB" --no-owner --no-acl' < loefsys-before-docker.dump

#. Check which migrations are still to run, without changing anything::

    $ docker compose run --rm web python manage.py migrate --plan

   For a database from ``feat/production-settings`` this lists exactly these, and nothing from before them: ``events.0004`` and ``0005``, ``members.0008_verbose_names``, ``0008_backfill_required_skipperships``, ``0008_admin_permission`` and ``0009_merge_0008``, and ``reservations.0003`` and ``0004``. If it lists anything older, such as an ``0001_initial``, the migration history differs from the code; stop and reconcile it first (see the pre-flight checklist).

#. Take a backup of the restored copy and migrate::

    $ ./infra/scripts/backup-db.sh
    $ docker compose run --rm web python manage.py migrate --no-input

   What these migrations do to existing data: staff users get the new "Admin" permission (the staff flag is removed), members who hold a skippership get any missing lower ones in its chain, groups and users who could change events get every event category permission, an "Activity managers" group is created, and the unused duplicate ``Reservation.status`` column is dropped (``request_status`` and ``denial_reason`` stay).

#. Copy uploaded files (``MEDIA_ROOT`` on the old host) into the ``media_data`` volume, then start the site::

    $ docker compose cp <old-media-dir>/. web:/app/media/
    $ docker compose up -d

   ``docker compose cp`` needs the ``web`` container to exist; run ``docker compose up -d`` first if it doesn't. Afterwards, make sure the files are owned by the app user: ``docker compose exec -u root web chown -R loefsys:loefsys /app/media``.

#. Point Apache at ``127.0.0.1:8000`` (see below), log in, and check the admin and a few member pages.

To try this on your own machine first, set ``DJANGO_SECURE_SSL_REDIRECT=false`` in a local ``.env`` and browse to ``http://localhost:8000``, or send ``X-Forwarded-Proto: https`` yourself.

Reverse proxy
-------------
No Apache config lives in this repository -- there's nothing to template or automate. As a one-time manual step, point the existing vhost's proxy directive at ``127.0.0.1:8000`` (matching the port mapping in ``docker-compose.yml``), keeping its current TLS-termination and ``X-Forwarded-Proto`` behaviour, which ``SECURE_PROXY_SSL_HEADER`` in ``loefsys/settings.py`` already expects.

HTTPS only
----------
Plain HTTP is only for local development. The ``.env`` examples set ``DJANGO_SECURE_SSL_REDIRECT=true``, so Django redirects any request that did not arrive over HTTPS, and session and CSRF cookies are always marked secure. Apache must therefore keep terminating TLS and setting ``X-Forwarded-Proto: https``; without that header every page redirects to itself. The container's healthcheck (``infra/scripts/healthcheck.py``) sends the same headers Apache does, so it is not affected.

Rollback
--------
GHCR keeps every tagged image. Rolling back does not need a rebuild -- on the host, in the compose project directory::

    $ IMAGE_TAG=<previous-good-tag> docker compose up -d

If the bad release also shipped a migration, reverting it is a **separate, manual** step (``manage.py migrate <app> <previous_migration>``) -- deliberately not automated, for the same reason unattended ``migrate`` isn't allowed until the pre-flight checklist's migration-reconciliation step is done.

See also
--------
``infra/README.md`` covers the same material from the perspective of someone already SSHed into a host, without needing to go read this page.
