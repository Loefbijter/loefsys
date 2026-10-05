"""Module keeping the compiled translation catalogues up to date.

Only the ``.po`` catalogues are in git. The ``.mo`` files Django reads are built from
them with ``compilemessages``: in the Docker image, in CI, and automatically before
the tests run and when ``runserver`` starts or a ``.po`` file changes.
"""

import logging
import os
from pathlib import Path

from django.conf import settings
from django.core import checks
from django.core.management import CommandError, call_command
from django.test.signals import setting_changed
from django.utils.autoreload import DJANGO_AUTORELOAD_ENV


def stale_catalogues() -> list[Path]:
    """Return the ``.po`` files whose ``.mo`` is missing or older."""
    stale = []
    for po in sorted(Path(settings.LOCALE_DIR).glob("*/LC_MESSAGES/*.po")):
        mo = po.with_suffix(".mo")
        if not mo.exists() or mo.stat().st_mtime < po.stat().st_mtime:
            stale.append(po)
    return stale


def compile_stale_catalogues() -> None:
    """Run ``compilemessages`` when a catalogue changed since it was last compiled."""
    if not stale_catalogues():
        return
    call_command("compilemessages", verbosity=0)
    # Forget catalogues that were already loaded without the new .mo files, the
    # same way Django's test tools do when LOCALE_PATHS changes.
    setting_changed.send(
        sender=None, setting="LOCALE_PATHS", value=settings.LOCALE_PATHS, enter=False
    )


def check_compiled_catalogues(**_):
    """Warn when the translations shown would be missing or out of date."""
    if os.environ.get(DJANGO_AUTORELOAD_ENV) == "true":
        return []  # runserver compiles them itself, see compile_on_autoreload().
    return [
        checks.Warning(
            f"{po.relative_to(settings.BASE_DIR)} is not compiled or has changed.",
            hint="Run `uv run manage.py compilemessages` (needs GNU gettext).",
            id="loefsys.W001",
        )
        for po in stale_catalogues()
    ]


def compile_on_autoreload(sender, **_):
    """Compile when ``runserver`` starts, and restart it when a ``.po`` file changes.

    Connected to ``autoreload_started``, so this runs in ``runserver``'s reloader.
    """
    sender.watch_dir(settings.LOCALE_DIR, "**/*.po")
    try:
        compile_stale_catalogues()
    except CommandError as error:
        logging.getLogger(__name__).warning("Could not compile translations: %s", error)
