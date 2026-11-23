Getting Started
===============
On this page, you will find instructions on how to set up your coding environment to contribute to the project.

Prerequisites
-------------
In order to contribute to the project, you should have the following prerequisites:

#. Install `Git <https://git-scm.com/>`_ and `GNU gettext <https://www.gnu.org/software/gettext/>`_ (``apt install gettext`` or ``brew install gettext``), which builds the translations. ``runserver`` and the tests compile them automatically.

#. Install `UV <https://docs.astral.sh/uv/>`_ by following the installation instructions `here <https://docs.astral.sh/uv/getting-started/installation/>`_.

#. Make sure you have Python 3.12, 3.13 or 3.14. Python 3.15 does not work yet, because ``psycopg-binary`` has no wheels for it. You can check which version you are running by executing the following command in your terminal::

    $ python --version

   If you don't have a suitable version, uv can install one for you::

    $ uv python install 3.14

#. Clone the repository locally by executing the following command::

    $ git clone https://github.com/Loefbijter/loefsys.git # If you prefer ssh, use:
    $ git clone git@github.com:Loefbijter/loefsys.git

#. Then, open the directory with the cloned repository and execute::

    $ uv sync --locked

#. Install all pre-commit hooks with the following command::

    $ pre-commit install  # If pre-commit isn't recognized, use this:
    $ uv run pre-commit install

#. In the root directory, create a ``.env`` file and fill it with the necessary environment variables. In :ref:`recommended-env`, the recommended environment variables for development can be found. **Make sure to have all recommended environment variables set or the server will not run!**

#. Create the database tables with the following command::

    $ uv run manage.py migrate

#. Next, start the Tailwind CSS watcher with the command below. The first time, it downloads the Tailwind binary for you, so you don't need Node.js::

    $ uv run manage.py tailwind

#. Finally, you can start the development server in a new terminal with::

    $ uv run manage.py runserver

#. Now, head over to `localhost:8000 <http://localhost:8000>`_ in your browser. You will see the login page, because every page except the login page needs you to be logged in. Read on to fill your database and create a user.

Filling the Database with Test Data
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The ``reset_staging`` command wipes your database and fills it with invented members, groups, skipperships, boats, events and reservations. It is the same command the staging server runs after every deploy. It refuses to run unless ``LOEFSYS_ALLOW_RESET=true`` is set, so only set that variable for the command itself, never in a production environment::

    $ LOEFSYS_ALLOW_RESET=true LOEFSYS_STAGING_PASSWORD=<password> uv run manage.py reset_staging

Afterwards, log in as ``admin@example.org`` (a superuser) or ``lid1@example.org`` (a regular member) with the password you chose. Without ``LOEFSYS_STAGING_PASSWORD``, the command generates a password and prints it.

Creating a Superuser
^^^^^^^^^^^^^^^^^^^^

#. If you want to create an admin user for yourself in your local database, you can run the following command::

    $ uv run manage.py createsuperuser

    # You will be asked for an email address and a password. The email address is what you log in with.
    # If you get a prompt that your password is too weak, you can ignore this (only in development of course, we don't do weak passwords in production ;).

#. You just created your first superuser! Head over to http://localhost:8000/login/ and log in with the credentials which you have entered in the previous step.

Running the Tests
-----------------

#. Run the unit tests with::

    $ uv run manage.py test

#. The end-to-end tests click through the site in a real browser with `Playwright <https://playwright.dev/python/>`_. They need the built stylesheet and a one-time browser install::

    $ uv run manage.py tailwind --minify
    $ uv run playwright install chromium
    $ uv run pytest e2e

   See ``e2e/README.md`` for more options, such as watching the browser or running the tests without access to jsDelivr (which is the only time you need Node.js).

#. Before pushing, run the same checks as CI::

    $ uv run ruff check .
    $ uv run ruff format --check .
    $ uv run mypy
