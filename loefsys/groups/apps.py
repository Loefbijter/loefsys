"""Module containing the configuration for the groups app."""

from django.apps import AppConfig


class GroupsConfig(AppConfig):
    """The app configuration for the groups."""

    name = "loefsys.groups"

    def ready(self):
        """Import signal handlers when the app is ready.

        Placed inside ready() to avoid import-time side-effects.
        """
        try:
            from . import signals  # noqa: F401, PLC0415
        except Exception:
            # If signals cannot be imported (e.g., during migrations), fail silently.
            pass
