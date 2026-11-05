"""Module containing the Celery tasks for reservations."""

from celery import shared_task

from loefsys.reservations import reminders


@shared_task(ignore_result=True)
def send_logbook_reminders() -> int:
    """Email members whose finished boat reservation still has no logbook."""
    return reminders.send_logbook_reminders()
