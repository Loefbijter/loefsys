Useful Commands
===============
This page contains a reference of useful commands.

Project-specific Commands
-------------------------
* Sync your virtual env with the lock file::

    uv sync --locked

* Sync your virtual env including optional dependencies for docs generation::

    uv sync --locked --all-groups

* Run the formatter::

    uv run ruff format

* Run the linter::

    uv run ruff check

* Run the mypy typechecker (checks the whole ``loefsys`` package, like CI)::

    uv run mypy

* Run the end-to-end browser tests (see ``e2e/README.md``)::

    uv run playwright install chromium  # once
    uv run pytest e2e

* Update the Dutch translation catalogue after adding or changing strings (see ``locale/README.rst``)::

    uv run manage.py makemessages

* Compile the translations (``runserver`` and the tests do this automatically)::

    uv run manage.py compilemessages

* Wipe the database and fill it with invented test data (refuses to run without ``LOEFSYS_ALLOW_RESET=true``)::

    LOEFSYS_ALLOW_RESET=true uv run manage.py reset_staging

* Generate docs locally::

    uv run manage.py generate_docs

Django-specific Commands
------------------------
See `django-admin <https://docs.djangoproject.com/en/5.2/ref/django-admin/>` for a complete list of built-in Django commands.

* Make migrations based on model changes::

    uv run manage.py makemigrations

* Push generated migrations to the database::

    uv run manage.py migrate

* Run the tests on a test database::

    uv run manage.py test

* Register a superuser in the currently configured database::

    uv run manage.py createsuperuser

* Start the Django development server::

    uv run manage.py runserver

* Start the Tailwind CSS watcher::

    uv run manage.py tailwind

* Build the minified stylesheet once, without watching::

    uv run manage.py tailwind --minify
