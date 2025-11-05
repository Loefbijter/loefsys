Getting Started
===============
On this page, you will find instructions on how to set up your coding environment to contribute to the project.

Prerequisites
-------------
In order to contribute to the project, you should have the following prerequisites:

#. Install `Git <https://git-scm.com/>`_ and `Node.js <https://nodejs.org/>`_.
#. Ensure you have Python 3.12 installed or higher. You can check which version you are running by executing the following command in your terminal::

    $ python --version

#. Install `UV <https://docs.astral.sh/uv/>`_ by following the installation instructions `here <https://docs.astral.sh/uv/getting-started/installation/>`_.
#. Clone the repository locally by executing the following command::

    $ git clone https://github.com/Loefbijter/loefsys.git

#. Then, open the directory with the cloned repository and execute::

    $ uv sync

#. Install all pre-commit hooks with the following command::

    $ pre-commit install  # If pre-commit isn't recognized, use this:
    $ uv run pre-commit install

#. In the root directory, create a ``.env`` file and fill it with the necessary environment variables. In :ref:`recommended-env`, the recommended environment variables for development can be found.
#. Setup Tailwind locally with the following command:

    $ uv run manage.py tailwind install

#. To populate the database, in the root folder, run the following command::

    $ uv run manage.py makemigrations

#. Then run the following command::

    $ uv run manage.py migrate

#. Finally, you can start the development server in a new terminal with::

    $ uv run manage.py tailwind dev

#. Now, head over to `localhost:8000 <localhost:8000>`_ in your browser and you should see the homepage of loefsys, or go to http://localhost:8000/profile/signup/.

Creating a Superuser
^^^^^^^^^^^^^^^^^^^^

#. If you want to create an admin user for yourself in your local database, you can run the following command::

    $ uv run manage.py createsuperuser

    # You will be asked to enter a username, email address, and password. Choose these as you like. You can keep the email address field empty.
    # If you get a prompt that your password is too weak, you can ignore this (only in development of course, we don't do weak passwords in production ;).

#. You just created your first superuser! Head over to http://localhost:8000/profile/login/ and log in with the credentials which you have entered in the previous step.
