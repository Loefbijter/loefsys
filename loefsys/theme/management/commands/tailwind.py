"""Module containing the command for integration with pytailwindcss."""

import sys
from typing import Any

import pytailwindcss
from django.conf import settings
from django.core.management import BaseCommand


class Command(BaseCommand):
    """The class that defines the command."""

    help = "Run the Tailwind watcher"

    def add_arguments(self, parser):
        """Register arguments for the command."""
        parser.add_argument("-w", "--watch", action="store_true")
        parser.add_argument("-m", "--minify", action="store_true")

    def handle(self, *_: tuple[Any, ...], **options: dict[str, object]) -> str | None:
        """Perform the actual logic of the command."""
        ipath = settings.BASE_DIR / "styles" / "globals.css"
        opath = settings.STATICFILES_DIRS[0] / "styles.css"
        args = ["-i", ipath, "-o", opath]
        if options["minify"]:
            args += ["--minify"]
        if options["watch"] or not options["minify"]:
            # We want watching to be the default.
            args += ["--watch"]

        try:
            pytailwindcss.run(
                args,
                live_output=True,
                auto_install=True,
                version=settings.TAILWIND_VERSION,
            )
        except KeyboardInterrupt:
            sys.exit(0)
