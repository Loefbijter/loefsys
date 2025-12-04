"""Module containing the command for integration with pytailwindcss."""

import sys
from typing import Any

import pytailwindcss
from django.core.management import BaseCommand

from loefsys.theme import settings


class Command(BaseCommand):
    """The class that defines the command."""

    help = "Run the Tailwind watcher"

    def add_arguments(self, parser):
        """Register arguments for the command."""
        parser.add_argument("-w", "--watch", action="store_true")
        parser.add_argument("-m", "--minify", action="store_true")

    def handle(self, *_: tuple[Any, ...], **options: dict[str, object]) -> str | None:
        """Perform the actual logic of the command."""
        args = ["-i", settings.TAILWIND_INPUT_CSS, "-o", settings.TAILWIND_OUTPUT_CSS]
        if options["minify"]:
            args += ["--minify"]
        if options["watch"] or not options["minify"]:
            # We want watching to be the default.
            args += ["--watch"]

        bin_path = settings.TAILWIND_BIN_PATH
        try:
            pytailwindcss.run(
                args,
                bin_path=bin_path,
                live_output=True,
                auto_install=False if bin_path else True,
                version=settings.TAILWIND_VERSION,
            )
        except KeyboardInterrupt:
            sys.exit(0)
