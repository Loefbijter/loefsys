"""Module defining the configuration for various security parameters."""

from collections.abc import Sequence

from cbs import env

from .auth import AuthSettings
from .base import BaseSettings

denv = env["DJANGO_"]

class SecuritySettings(AuthSettings, BaseSettings):
    """Class defining the configuration for various security parameters."""

    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_HTTPONLY = True
    CSRF_COOKIE_SECURE = True

    # Ramped deliberately: app.loefbijter.nl is a young hostname and HSTS
    # cannot be retracted once browsers cache it. Raise after a week clean.
    SECURE_HSTS_SECONDS = 300
    SECURE_HSTS_INCLUDE_SUBDOMAINS = False
    SECURE_HSTS_PRELOAD = False
    SECURE_CONTENT_TYPE_NOSNIFF = True

    # Apache terminates TLS and sets X-Forwarded-Proto; without this Django
    # believes every request is plain HTTP.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    CSRF_TRUSTED_ORIGINS = denv.list([])

    def MIDDLEWARE(self) -> Sequence[str]:  # noqa N802
        return (
            "django.middleware.security.SecurityMiddleware",
            "django.middleware.clickjacking.XFrameOptionsMiddleware",
            *super().MIDDLEWARE(),
        )
