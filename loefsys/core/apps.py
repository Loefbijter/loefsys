"""Module containing the app definition for the core module."""

from django.apps import AppConfig
from django.core import checks
from django.utils.autoreload import autoreload_started

from loefsys.core.translations import check_compiled_catalogues, compile_on_autoreload


class CoreConfig(AppConfig):
    """Configuration for the core."""

    name = "loefsys.core"

    def ready(self):
        """Register the system checks and compile translations in ``runserver``."""
        checks.register(check_compiled_catalogues)
        autoreload_started.connect(compile_on_autoreload)
