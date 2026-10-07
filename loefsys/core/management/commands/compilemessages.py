"""Module overriding ``compilemessages`` to skip third-party directories."""

from django.core.management.commands import compilemessages


class Command(compilemessages.Command):
    """Compile the catalogues in ``locale/``. See ``locale/README.rst``."""

    def add_arguments(self, parser):
        """Leave the virtualenv and ``node_modules`` alone."""
        super().add_arguments(parser)
        parser.set_defaults(ignore_patterns=["node_modules", ".venv"])
