"""Module containing the app definition for the synchronization module."""

from django.apps import AppConfig


class SyncConfig(AppConfig):
    """Configuration for the sync app."""

    name = "loefsys.sync"

    def ready(self):
        """Run when Django starts."""
        from . import signals

        return signals
