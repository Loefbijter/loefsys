"""Module defining the management command to generate docs."""

import subprocess
from typing import Any

from django.core.management import BaseCommand


class Command(BaseCommand):
    """The class that defines the code to generate docs."""

    help = "Runs the sphinx-apidoc and sphinx-build commands to generate docs"

    def handle(self, *_: tuple[Any, ...], **__: dict[str, object]) -> str | None:
        """Perform the actual logic of the command."""
        subprocess.run(self._apidoc_args(), check=False)
        subprocess.run(self._build_args(), check=False)

    @staticmethod
    def _apidoc_args():
        flags = (
            "-o",
            "./docs/api",  #   Directory to place the output files. If it does not
            #                  exist, it is created.
            "-f",  #           Force overwriting of any existing generated files.
            "-e",  #           Put documentation for each module on its own page.
            "--remove-old",  # Remove existing files in the output directory that are
            #                  not created anymore. Not compatible with --full.
            "-M",  #           Put module documentation before submodule documentation.
        )

        exclude = ("./loefsys/*/migrations", "./loefsys/manage.py", "./loefsys/*/tests")

        return "uv", "run", "sphinx-apidoc", *flags, "./loefsys", *exclude

    @staticmethod
    def _build_args():
        flag_m = ("-M", "html")  # Select a builder, using the make-mode.
        # Sphinx only recognizes the -M option if it is used first, along with the
        # source and output dirs, before any other options are passed. For example:
        #   sphinx-build -M html ./source ./build --fail-on-warning

        flags = (
            "-E",  # Don't use a saved environment (the structure caching all
            #        cross-references), but rebuild it completely.
        )
        return "uv", "run", "sphinx-build", *flag_m, "./docs", "./docs/_build", *flags
