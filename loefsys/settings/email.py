"""Module containing the configuration for the email service."""

from pathlib import Path

from cbs import env

denv = env["DJANGO_"]


class EmailSettings:
    """Class containing the configuration for the email service."""

    EMAIL_BACKEND = denv("django.core.mail.backends.filebased.EmailBackend")
    EMAIL_FILE_PATH = Path(__file__).resolve().parent.parent.parent / "sent_emails"

    EMAIL_HOST = denv("")
    EMAIL_PORT = denv.int(587)
    EMAIL_HOST_USER = denv("")
    EMAIL_HOST_PASSWORD = denv("")
    EMAIL_USE_TLS = denv.bool(True)

    EMAIL_TIMEOUT = 5

    DEFAULT_FROM_EMAIL = "Loefbijter <noreply@loefbijter.nl>"
    EMAIL_SUBJECT_PREFIX = "[Loefbijter]"

    def SERVER_EMAIL(self) -> str:  # noqa: D102, N802
        return self.DEFAULT_FROM_EMAIL
