"""Module overriding ``makemessages`` with this project's defaults.

The catalogue is edited on many branches at once, so it is written to change only
when the translatable strings do: no source locations, no creation date, and the
entries sorted by message id rather than by where they appear in the code.
"""

import re
from pathlib import Path

from django.core.management.commands import makemessages

Base = makemessages.Command

POT_CREATION_DATE = re.compile(r'^"POT-Creation-Date: .*\\n"\n', re.MULTILINE)


class Command(Base):
    """Update the Dutch catalogue in ``locale/``. See ``locale/README.rst``."""

    msgmerge_options = [*Base.msgmerge_options, "--sort-output"]  # noqa: RUF012
    msgattrib_options = [*Base.msgattrib_options, "--sort-output"]  # noqa: RUF012

    def add_arguments(self, parser):
        """Make Dutch, no locations and no obsolete entries the defaults."""
        super().add_arguments(parser)
        parser.set_defaults(
            locale=["nl"],
            no_location=True,
            no_obsolete=True,
            ignore_patterns=["node_modules", ".venv"],
        )

    def write_po_file(self, potfile, locale):
        """Write the catalogue, then drop the header that changes on every run."""
        super().write_po_file(potfile, locale)
        pofile = Path(potfile).parent / locale / "LC_MESSAGES" / f"{self.domain}.po"
        text = pofile.read_text(encoding="utf-8")
        pofile.write_text(POT_CREATION_DATE.sub("", text, count=1), encoding="utf-8")
