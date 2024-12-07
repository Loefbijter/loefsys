Getting Started
===============
On this page, you will find instructions on how to set up your coding environment to contribute to the project.

Prerequisites
-------------
In order to contribute to the project, you should have the following prerequisites:

#. Install `Git <https://git-scm.com/>`_.
#. Ensure you have Python 3.12 installed or higher. You can check which version you are running by executing the following command in your terminal::

    $ python --version

#. Install `UV <https://docs.astral.sh/uv/>`_ by following the installation instructions `here <https://docs.astral.sh/uv/getting-started/installation/>`_.
#. Clone the repository locally by executing the following command::

    $ git clone https://github.com/Loefbijter/loefsys.git

#. Then, open the directory with the cloned repository and execute::

    $ uv install

#. Install all pre-commit hooks with the following command::

    $ pre-commit install  # If pre-commit isn't recognized, use this:
    $ uv run pre-commit install

#. In the root directory, make a ``.env`` file and fill it with the necessary environment variables. In :ref:`recommended-env`, the recommended environment variables for development can be found.
#. Finally, you can start the development server with::

    $ uv run manage.py runserver

#. Now, head over to `localhost:8000 <localhost:8000>` in your browser and you should see the homepage of loefsys.

Creating a Superuser
^^^^^^^^^^^^^^^^^^^^

#. If you want to create an admin user for yourself in your local database, you can run the following command::

    $ uv run manage.py createsuperuser

    # You will be asked to enter a username, email address, and password. Choose these as you like. You can keep the email address field empty.
    # If you get a prompt that your password is too weak, you can ignore this (only in development of course, we don't do weak passwords in production ;)).

#. You just created your first superuser! Head over to http://localhost:8000/accounts/login/ and log in with the credential which you have entered in the previous step.

Available Commands
------------------

* :func:`uv run manage.py format <loefsys.scripts.format>`
* :func:`uv run manage.py lint <loefsys.scripts.lint>`
* :func:`uv run manage.py typecheck <loefsys.scripts.typecheck>`
* :func:`uv run manage.py runserver <loefsys.scripts.runserver>`
* :func:`uv run manage.py makemigrations <loefsys.scripts.makemigrations>`
* :func:`uv run manage.py migrate <loefsys.scripts.migrate>`
* :func:`uv run manage.py createsuperuser <loefsys.scripts.createsuperuser>`
* :func:`uv run manage.py collectstatic <loefsys.scripts.collectstatic>`
* :func:`uv run manage.py makedocs <loefsys.scripts.makedocs>`
