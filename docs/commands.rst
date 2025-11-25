Useful Commands
===============
This page contains a reference of useful commands.

Project-specific Commands
-------------------------
* Sync your virtual env with the lock file::

    uv sync --locked

* Run the formatter::

    uv run ruff format

* Run the linter::

    uv run ruff check

* Run the mypy typechecker::

    uv run mypy -p loefsys

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

* Start the Tailwind development server::

    uv run manage.py tailwind dev

* Start the Django dev server and Tailwind dev server in one command::

    uv run manage.py tailwind start
