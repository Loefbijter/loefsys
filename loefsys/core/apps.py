"""Module containing the app definition for the core module."""

from django.apps import AppConfig
from django.core import checks

from loefsys.core.translations import check_compiled_catalogues


class CoreConfig(AppConfig):
    """Configuration for the core."""

    name = "loefsys.core"

    def ready(self):
        """Register the system checks."""
        checks.register(check_compiled_catalogues)
