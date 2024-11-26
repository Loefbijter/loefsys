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
    * Set ``DJANGO_DEBUG=1`` to set this variable to ``True``.
    * Used to set the variable `DEBUG <https://docs.djangoproject.com/en/5.0/ref/settings/#debug>`_. Sets `INTERNAL_IPS <https://docs.djangoproject.com/en/5.0/ref/settings/#internal-ips>`_ to ``["127.0.0.1", "localhost"]`` when debugging is enabled and to ``[]`` when disabled. Also enables or disables `Django debug toolbar <https://django-debug-toolbar.readthedocs.io/en/latest/>`_.

* ``DJANGO_SECRET_KEY``

    .. IMPORTANT:: Must be defined as environment variable. No default is provided.

    * Used to set the variable `SECRET_KEY <https://docs.djangoproject.com/en/5.0/ref/settings/#secret-key>`_. For development, set this string to any desired. For production, the secret key must not have the prefix ``"django-insecure-"``, the minimum length must be at least 50 characters, with a minimum of 5 unique characters.

* ``DJANGO_DATABASE_URL``

    * Default: ``"sqlite://:memory:"``
    * Set to ``DJANGO_DATABASE_URL=sqlite:///db.sqlite`` to use a database file that persists in development. Use ``DJANGO_DATABASE_URL=postgres://<USER>:<PASSWORD>@<HOST>:<PORT>/<NAME>`` to use a Postgres server for example. Read `dj_database_url <https://github.com/jazzband/dj-database-url>`_ for examples to connect with other databases.

* ``DJANGO_DATABASE_CONN_MAX_AGE``

    * Default: ``60``
    * Used to set the variable `CONN_MAX_AGE <https://docs.djangoproject.com/en/5.0/ref/settings/#conn-max-age>`_.

* ``DJANGO_TIME_ZONE``

    * Default: ``"Europe/Amsterdam"``
    * Used to set the variable `TIME_ZONE <https://docs.djangoproject.com/en/5.0/ref/settings/#time-zone>`_.

AWS
^^^

* ``AWS_STORAGE_BUCKET_NAME``

    * Default: ``None``
    * If not defined, the standard `StaticFilesStorage <https://docs.djangoproject.com/en/5.0/ref/contrib/staticfiles/#django.contrib.staticfiles.storage.StaticFilesStorage>`_ and `FileSystemStorage <https://docs.djangoproject.com/en/5.0/ref/files/storage/#django.core.files.storage.FileSystemStorage>`_ are used for static files and media, respectively.

.. _recommended-env:

Recommended Development Variables
---------------------------------

For development, it is recommended to start with the following variables set in your environment::

    DJANGO_SECRET_KEY=CustomString
    DJANGO_DEBUG=1
    DJANGO_DATABASE_URL=sqlite:///db.sqlite

Then, depending on which part of the project is being developed, it is possible to customize this to suit your own needs.
