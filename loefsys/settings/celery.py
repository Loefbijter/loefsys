"""Module containing the configuration for Celery.

The broker is read by Celery from the ``CELERY_BROKER_URL`` environment variable.
"""

from typing import Any

from celery.schedules import crontab

from .locale import LocaleSettings


class CelerySettings(LocaleSettings):
    """Class containing the configuration for Celery and its periodic tasks."""

    def CELERY_TIMEZONE(self) -> str:  # noqa N802 D102
        return self.TIME_ZONE

    def CELERY_BEAT_SCHEDULE(self) -> dict[str, dict[str, Any]]:  # noqa N802 D102
        return {
            "send-logbook-reminders": {
                "task": "loefsys.reservations.tasks.send_logbook_reminders",
                # Every hour during the day, so nobody gets an email at night.
                "schedule": crontab(minute="0", hour="8-21"),
            }
        }
