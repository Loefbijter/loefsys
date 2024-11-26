# Getting Started

On this page, you will find instructions on how to set up your coding
environment to contribute to the project.

## Prerequisites

In order to contribute to the project, you should have the following
prerequisites:

1.  Install [Git](https://git-scm.com/).

2.  Ensure you have Python 3.12 installed or higher. You can check which
    version you are running by executing the following command in your
    terminal:

        $ python --version

3.  Install [Poetry](https://python-poetry.org/) by following the
    installation instructions
    [here](https://python-poetry.org/docs/#installation).

4.  Clone the repository locally by executing the following command:

        $ git clone https://github.com/Loefbijter/loefsys.git

5.  Then, open the directory with the cloned repository and execute:

        $ poetry install

6.  Install all pre-commit hooks with the following command:

        $ pre-commit install  # If pre-commit isn't recognized, use this:
        $ poetry run pre-commit install

7.  In the root directory, make a `.env` file and fill it with the
    necessary environment variables. In
    `recommended-env`{.interpreted-text role="ref"}, the recommended
    environment variables for development can be found.

8.  Finally, you can start the development server with:

        $ poetry run runserver

9.  Now, head over to [localhost:8000 \<localhost:8000\>]{.title-ref} in
    your browser and you should see the homepage of loefsys.

### Creating a Superuser

1.  If you want to create an admin user for yourself in your local
    database, you can run the following command:

        $ poetry run createsuperuser

        # You will be asked to enter a username, email address, and password. Choose these as you like. You can keep the email address field empty.
        # If you get a prompt that your password is too weak, you can ignore this (only in development of course, we don't do weak passwords in production ;)).

2.  You just created your first superuser! Head over to
    <http://localhost:8000/accounts/login/> and log in with the
    credential which you have entered in the previous step.

## Available Commands

-   `poetry run format <loefsys.scripts.format>`{.interpreted-text
    role="func"}
-   `poetry run lint <loefsys.scripts.lint>`{.interpreted-text
    role="func"}
-   `poetry run typecheck <loefsys.scripts.typecheck>`{.interpreted-text
    role="func"}
-   `poetry run runserver <loefsys.scripts.runserver>`{.interpreted-text
    role="func"}
-   `poetry run makemigrations <loefsys.scripts.makemigrations>`{.interpreted-text
    role="func"}
-   `poetry run migrate <loefsys.scripts.migrate>`{.interpreted-text
    role="func"}
-   `poetry run createsuperuser <loefsys.scripts.createsuperuser>`{.interpreted-text
    role="func"}
-   `poetry run collectstatic <loefsys.scripts.collectstatic>`{.interpreted-text
    role="func"}
-   `poetry run makedocs <loefsys.scripts.makedocs>`{.interpreted-text
    role="func"}
