Environment Variables
=====================
This page contains a complete list of the available environment variables, including their defaults and recommended settings for both development and production.

List of Environment Variables
-----------------------------

This is the current complete list of available environment variables. As more environment variables are added to to project, they will be added to this list.

Django
^^^^^^
* ``DJANGO_DEBUG``

    * Default: ``False``
    * Set ``DJANGO_DEBUG=1`` to set this variable to ``True``. Boolean variables accept ``1``/``true``/``yes``/``on`` and ``0``/``false``/``no``/``off``; any other value stops the server with an error.
    * Used to set the variable `DEBUG <https://docs.djangoproject.com/en/5.2/ref/settings/#debug>`_. Sets `INTERNAL_IPS <https://docs.djangoproject.com/en/5.0/ref/settings/#internal-ips>`_ to ``["127.0.0.1", "localhost"]`` when debugging is enabled and to ``[]`` when disabled. Also enables or disables `Django debug toolbar <https://django-debug-toolbar.readthedocs.io/en/latest/>`_.

* ``DJANGO_BROWSER_RELOAD_ENABLED``

    * Default: ``False``
    * Set ``DJANGO_BROWSER_RELOAD_ENABLED=1`` to turn on the dev browser auto-reload helper while debugging.
    * Keeps ``django-browser-reload`` installed in the project without forcing it to run when not wanted.

* ``DJANGO_SECRET_KEY``

    .. IMPORTANT:: Must be defined as environment variable. No default is provided.

    * Used to set the variable `SECRET_KEY <https://docs.djangoproject.com/en/5.2/ref/settings/#secret-key>`_. For development, set this string to any desired. For production, the secret key must not have the prefix ``"django-insecure-"``, the minimum length must be at least 50 characters, with a minimum of 5 unique characters.

* ``DJANGO_DATABASE_URL``

    * Default: ``"sqlite://:memory:"``
    * Set to ``DJANGO_DATABASE_URL=sqlite:///db.sqlite`` to use a database file that persists in development. Use ``DJANGO_DATABASE_URL=postgres://<USER>:<PASSWORD>@<HOST>:<PORT>/<NAME>`` to use a Postgres server for example. Read `dj_database_url <https://github.com/jazzband/dj-database-url>`_ for examples to connect with other databases.

* ``DJANGO_DATABASE_CONN_MAX_AGE``

    * Default: ``60``
    * Used to set the variable `CONN_MAX_AGE <https://docs.djangoproject.com/en/5.2/ref/settings/#conn-max-age>`_.

* ``DJANGO_ALLOWED_HOSTS``

    * Default: empty
    * A comma-separated list used to set the variable `ALLOWED_HOSTS <https://docs.djangoproject.com/en/5.2/ref/settings/#allowed-hosts>`_. While debugging, Django allows ``localhost`` by itself.

* ``DJANGO_CSRF_TRUSTED_ORIGINS``

    * Default: empty
    * A comma-separated list used to set the variable `CSRF_TRUSTED_ORIGINS <https://docs.djangoproject.com/en/5.2/ref/settings/#csrf-trusted-origins>`_, for example ``https://app.loefbijter.nl``. Needed on staging and production, where the site is served over HTTPS behind a proxy.

* ``DJANGO_SECURE_SSL_REDIRECT``

    * Default: ``False``
    * Used to set the variable `SECURE_SSL_REDIRECT <https://docs.djangoproject.com/en/5.2/ref/settings/#secure-ssl-redirect>`_. Plain HTTP is only for local development: staging and production set this to ``True``, so every HTTP request is redirected to HTTPS.

* ``DJANGO_STATIC_MANIFEST``

    * Default: ``False``
    * Set to ``True`` to serve hashed, compressed static files through `WhiteNoise <https://whitenoise.readthedocs.io/>`_. The Docker image turns this on. It needs ``collectstatic`` to have run, so leave it off for local development and tests.

The time zone is fixed to ``Europe/Amsterdam`` and can't be changed through the environment.

Email
^^^^^

By default, emails are not sent but written to files in the ``sent_emails/`` folder, so you can read them during development.

* ``DJANGO_EMAIL_BACKEND``

    * Default: ``"django.core.mail.backends.filebased.EmailBackend"``
    * Used to set the variable `EMAIL_BACKEND <https://docs.djangoproject.com/en/5.2/ref/settings/#email-backend>`_. Set it to ``django.core.mail.backends.smtp.EmailBackend`` to send email through the SMTP server below.

* ``DJANGO_EMAIL_HOST``, ``DJANGO_EMAIL_PORT``, ``DJANGO_EMAIL_HOST_USER``, ``DJANGO_EMAIL_HOST_PASSWORD``

    * Defaults: empty, ``587``, empty, empty
    * The SMTP server to send through. Used to set `EMAIL_HOST <https://docs.djangoproject.com/en/5.2/ref/settings/#email-host>`_ and the related settings.

* ``DJANGO_EMAIL_USE_TLS``

    * Default: ``True``
    * Used to set the variable `EMAIL_USE_TLS <https://docs.djangoproject.com/en/5.2/ref/settings/#email-use-tls>`_.

AWS
^^^

* ``AWS_STORAGE_BUCKET_NAME``

    * Default: ``None``
    * If not defined, the standard `StaticFilesStorage <https://docs.djangoproject.com/en/5.2/ref/contrib/staticfiles/#django.contrib.staticfiles.storage.StaticFilesStorage>`_ and `FileSystemStorage <https://docs.djangoproject.com/en/5.0/ref/files/storage/#django.core.files.storage.FileSystemStorage>`_ are used for static files and media, respectively.

Tailwind
^^^^^^^^

* ``TAILWIND_BIN_PATH``

    * Default: ``None``
    * Path to a Tailwind CSS binary to use. If not defined, ``manage.py tailwind`` downloads the pinned Tailwind version by itself.

Staging
^^^^^^^

* ``LOEFSYS_ALLOW_RESET``

    * Default: unset
    * ``manage.py reset_staging`` wipes the database and refuses to run unless this is ``true``. Only the staging server (and your own machine, for a single run) should have it. **Never set it in production.**

* ``LOEFSYS_STAGING_PASSWORD``

    * Default: unset
    * The password ``reset_staging`` gives every invented user. If not defined, a random password is generated and printed.

.. _recommended-env:

Recommended Development Variables
---------------------------------

For development, it is recommended to start with the following variables set in your environment::

    DJANGO_SECRET_KEY=CustomString
    DJANGO_DEBUG=1
    DJANGO_DATABASE_URL=sqlite:///db.sqlite

Then, depending on which part of the project is being developed, it is possible to customize the environment variables to suit your own needs.
