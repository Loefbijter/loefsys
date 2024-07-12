from pathlib import Path

from cbs import BaseSettings as Settings
from cbs import env

denv = env["DJANGO_"]


class BaseSettings(Settings):
    BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent

    DEBUG = denv.bool(False)
    ALLOWED_HOSTS = denv.list("")

    ROOT_URLCONF = "loefsys.urls"
    WSGI_APPLICATION = "loefsys.wsgi.application"

    @denv
    def SECRET_KEY(self):  # noqa N802
        raise ValueError("Environment variable DJANGO_SECRET_KEY must be set.")

    def INTERNAL_IPS(self):  # noqa N802
        return ["localhost", "127.0.0.1"] if self.DEBUG else []

    def DJANGO_APPS(self):  # noqa N802
        return [
            "django.contrib.contenttypes",
        ]

    def THIRD_PARTY_APPS(self):  # noqa N802
        return ["debug_toolbar"] if self.DEBUG else []

    def LOCAL_APPS(self):  # noqa N802
        return [
            "loefsys.groups",
            "loefsys.reservations",
            "loefsys.events",
        ]

    def INSTALLED_APPS(self):  # noqa N802
        return self.DJANGO_APPS + self.THIRD_PARTY_APPS + self.LOCAL_APPS

    def MIDDLEWARE(self):  # noqa N802
        return ["debug_toolbar.middleware.DebugToolbarMiddleware"] if self.DEBUG else []
