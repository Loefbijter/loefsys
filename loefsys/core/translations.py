"""Module keeping the compiled translation catalogues up to date.

Only the ``.po`` catalogues are in git. The ``.mo`` files Django reads are built from
them with ``compilemessages``: in the Docker image, in CI, and automatically before
the tests run.
"""

from pathlib import Path

from django.conf import settings
from django.core import checks
from django.core.management import call_command
from django.test.signals import setting_changed


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
    return [
        checks.Warning(
            f"{po.relative_to(settings.BASE_DIR)} is not compiled or has changed.",
            hint="Run `uv run manage.py compilemessages` (needs GNU gettext).",
            id="loefsys.W001",
        )
        for po in stale_catalogues()
    ]
