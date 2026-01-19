"""Module containing the configuration for the email service."""

from pathlib import Path


class EmailSettings:
    """Class containing the configuration for the email service."""

    EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
    EMAIL_FILE_PATH = Path(__file__).resolve().parent.parent.parent / "sent_emails"
    # For console output csn be replaced with:
    # EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
    # Or for email output with:
    # EMAIL_HOST = "smtp.loefbijter.nl"         # Replace with your actual SMTP host
    # EMAIL_PORT = 587                          # or 465 for SSL
    # EMAIL_HOST_USER = "noreply@loefbijter.nl" # Your SMTP user (same as FROM email)
    # EMAIL_HOST_PASSWORD = "your-app-password" # Needs to be a real, secure password
    # EMAIL_USE_TLS = True                      # Or EMAIL_USE_SSL = True

    EMAIL_TIMEOUT = 5

    DEFAULT_FROM_EMAIL = "Loefbijter <noreply@loefbijter.nl>"
    EMAIL_SUBJECT_PREFIX = "[Loefbijter]"

    def SERVER_EMAIL(self) -> str:  # noqa: D102, N802
        return self.DEFAULT_FROM_EMAIL
