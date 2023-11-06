# Loefbijter System (LoefSys)

This repository is owned by the Nijmeegse student sailing association (N.S.Z.V.) De Loefbijter. The code in this repository facilitates the internal systems of De Loefbijter like our website, mobile app and (in the future) user management system.  

Any questions related to this repository should be directed towards the [website committee](mailto:webcie@loefbijter.nl).

This project uses the [Zappa](https://github.com/Miserlou/Zappa) and [Django](https://github.com/django/django) frameworks.

License: MIT

## Getting started
### Prerequisites
You should have
- The repository cloned locally, if you don't have this yet execute the command:

        $ git clone https://github.com/Loefbijter/loefsys.git
- An active [Docker installation](https://www.docker.com/products/docker-desktop/)
- Docker compose (is included in Docker Desktop)
- Command line
- Development environment (PyCharm or VSCode recommended)

### Setting up your environment
1. Make sure Docker (Desktop) is running and your command line directory is the root folder of this project.
2. Copy the file `infra/.env.example` and rename it to `infra/.env`. You do not need to change any of the variables.
3. That's it! To test if your environment is working run the following in your command line:

        $ docker compose up -d

This command starts the two main containers: the database and the webserver which runs Django.
4. Head over to [localhost:8000](localhost:8000) in your browser and you should see the homepage of loefsys. 

Congrats! You successfully set up your environment. Don't forget to shut down the container when you're finished using `$ docker compose down` and repeat step 3 and 4 to return to your environment.

### Creating a local superuser
A superuser is an administrator of the system. Such a user is necessary to create new reservations, groups, users, etc. for testing purposes. If you haven't yet created a superuser you can create one now.
1. Make sure your environment is up and running, if not then follow the steps as described in the section 'Setting up your environment'.
2. The loefsys container is its own separate operating system. To execute commands inside the container running the webserver execute the following command:

        $ docker exec -it loefsys-web-1 /bin/bash
   1. The `-it` flag tells docker to run an interactive (`i`) terminal (`t`) in which we can execute commands
   2. `loefsys-web-1` is the name of the webserver assigned by docker 

You should see that your command line has changed to `bash-*.*` which means that you are now successfully able to execute commands inside the container
5. If you haven't done this already, migrate the database by executing

        $ python manage.py migrate
6. Now create a new superuser by the following in the command window:

        $ python manage.py createsuperuser
   1. You will be asked to enter a username, email address, and password. Choose these as you like. You can keep the email address field empty.
   2. If you get a prompt that your password is too weak, you can ignore this (only in development of course, we don't do weak passwords in production ;)).

You just created your first superuser! Head over to http://localhost:8000/accounts/login/ and log in with the credential which you have entered in the previous step.
## Basic commands
### Setting Up Your Users

    $ zappa invoke --raw dev "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@yourdomain.com', 'password')"
### Type checks

Running type checks with mypy:

    $ mypy loefsys

### Test coverage

To run the tests, check your test coverage, and generate an HTML coverage report:

    $ coverage run -m pytest
    $ coverage html
    $ open htmlcov/index.html

#### Running tests with pytest

    $ pytest

### Live reloading and Sass CSS compilation

Moved to [Live reloading and SASS compilation](https://cookiecutter-django.readthedocs.io/en/latest/developing-locally.html#sass-compilation-live-reloading).

## Deployment

The following details how to deploy this application.
