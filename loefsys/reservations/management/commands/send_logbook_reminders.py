"""Management command to send the logbook reminders without Celery."""

from typing import Any

from django.core.management.base import BaseCommand

from loefsys.reservations.reminders import send_logbook_reminders


class Command(BaseCommand):
    """Email members whose finished boat reservation still has no logbook."""

    help = "Email members whose finished boat reservation still has no logbook."

    def handle(self, *_: tuple[Any, ...], **__: dict[str, object]) -> None:
        """Send the due reminders and report how many went out."""
        sent = send_logbook_reminders()
        self.stdout.write(f"Sent {sent} logbook reminder(s).")
