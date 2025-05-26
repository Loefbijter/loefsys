"""Module containing the base configuration."""

from collections.abc import Sequence
from pathlib import Path
from typing import cast

from cbs import BaseSettings as ClassySettings, env
from django_components import ComponentsSettings

denv = env["DJANGO_"]


class BaseSettings(ClassySettings):
    """Base class for settings configuration.

    The base class configures essential variables, such as the debug mode, which may be
    required by other modules.
    """

    BASE_DIR = Path(__file__).resolve().parent.parent.parent

    DEBUG = denv.bool(False)
    ALLOWED_HOSTS = denv.list("")

    ROOT_URLCONF = "loefsys.urls"
    WSGI_APPLICATION = "loefsys.wsgi.application"

    DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

    STATIC_URL = "static/"

    STATICFILES_FINDERS = [
        # Default finders
        "django.contrib.staticfiles.finders.FileSystemFinder",
        "django.contrib.staticfiles.finders.AppDirectoriesFinder",
        # Django components
        "django_components.finders.ComponentsFileSystemFinder",
    ]

    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

    @denv
    def SECRET_KEY(self) -> str:  # noqa N802 D102
        raise ValueError("Environment variable DJANGO_SECRET_KEY must be set.")

    def INTERNAL_IPS(self) -> Sequence[str]:  # noqa N802 D102
        return ("localhost", "127.0.0.1") if self.DEBUG else ()

    def DJANGO_APPS(self) -> Sequence[str]:  # noqa N802 D102
        return ("django.contrib.contenttypes",)

    def THIRD_PARTY_APPS(self) -> Sequence[str]:  # noqa N802 D102
        apps = ("django_components",)
        debug_apps = ("debug_toolbar",)
        return apps + debug_apps if self.DEBUG else apps

    def LOCAL_APPS(self) -> Sequence[str]:  # noqa N802 D102
        return (
            "loefsys.events",
            "loefsys.groups",
            "loefsys.reservations",
            "loefsys.users",
            "loefsys.indexpage",
            "loefsys.profile",
            "loefsys.accountinfopage",
        )

    def INSTALLED_APPS(self) -> Sequence[str]:  # noqa N802 D102
        return (
            *cast(Sequence[str], self.DJANGO_APPS),
            *cast(Sequence[str], self.THIRD_PARTY_APPS),
            *cast(Sequence[str], self.LOCAL_APPS),
        )

    def MIDDLEWARE(self) -> Sequence[str]:  # noqa N802 D102
        middleware = ("django_components.middleware.ComponentDependencyMiddleware",)
        debug_middleware = ("debug_toolbar.middleware.DebugToolbarMiddleware",)
        return middleware + debug_middleware if self.DEBUG else middleware
