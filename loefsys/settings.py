"""Django settings for the loefsys project.

Before the settings are loaded, a file named ``.env`` located in the root of the project
is loaded to populate the environment variables.
"""

import os
from pathlib import Path

import dj_database_url
from django.utils.translation import gettext_lazy as _
from dotenv import load_dotenv

load_dotenv()


def env_bool(key: str, default: bool) -> bool:
    """Read a boolean from the environment.

    Accepts ``y``, ``yes``, ``on``, ``t``, ``true`` and ``1`` as true and ``n``,
    ``no``, ``off``, ``f``, ``false`` and ``0`` as false, ignoring case. Any other
    value raises a ``ValueError`` so that a typo does not silently flip a setting.
    """
    value = os.environ.get(key)
    if value is None:
        return default
    value = value.strip().lower()
    if value in ("y", "yes", "on", "t", "true", "1"):
        return True
    if value in ("n", "no", "off", "f", "false", "0"):
        return False
    raise ValueError(f"Unrecognised value for {key}: {value!r}")


def env_list(key: str) -> list[str]:
    """Read a comma-separated list from the environment."""
    return [x.strip() for x in os.environ.get(key, "").split(",") if x.strip()]


BASE_DIR = Path(__file__).resolve().parent.parent

DEBUG = env_bool("DJANGO_DEBUG", False)
BROWSER_RELOAD_ENABLED = env_bool("DJANGO_BROWSER_RELOAD_ENABLED", False)

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Environment variable DJANGO_SECRET_KEY must be set.")

ALLOWED_HOSTS = env_list("DJANGO_ALLOWED_HOSTS")

ROOT_URLCONF = "loefsys.urls"
WSGI_APPLICATION = "loefsys.wsgi.application"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

INTERNAL_IPS = ["localhost", "127.0.0.1"] if DEBUG else []

# Applications

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.auth",
    "django.contrib.sessions",
    "django.contrib.messages",
    "loefsys.core.admin_apps.LoefsysAdminConfig",
    "django.contrib.staticfiles",
    "django_cotton",
    "compressor",
]
if DEBUG and BROWSER_RELOAD_ENABLED:
    INSTALLED_APPS.append("django_browser_reload")
if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")
INSTALLED_APPS += [
    "loefsys.core",
    "loefsys.events",
    "loefsys.groups",
    "loefsys.reservations",
    "loefsys.members",
    "loefsys.home",
    "loefsys.theme",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "loefsys.core.middleware.UserAgentMiddleware",
]
if DEBUG and BROWSER_RELOAD_ENABLED:
    MIDDLEWARE.append("django_browser_reload.middleware.BrowserReloadMiddleware")
MIDDLEWARE.append("loefsys.core.middleware.ErrorPageMiddleware")
if DEBUG:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")
MIDDLEWARE += [
    "django.contrib.sessions.middleware.SessionMiddleware",
    # Activate the language before any middleware that may render or redirect.
    "loefsys.core.i18n.LanguageMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    # Require login for anonymous users across most pages. Public paths are
    # whitelisted separately.
    "loefsys.core.middleware.RequireLoginMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

# Templates

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "loefsys.core.context_processors.is_mobile",
                "loefsys.core.context_processors.static_pages",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.tz",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
            ],
            "loaders": [
                (
                    "django.template.loaders.cached.Loader",
                    [
                        "django.template.loaders.filesystem.Loader",
                        "django.template.loaders.app_directories.Loader",
                    ],
                )
            ],
        },
    }
]

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# Database

DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DJANGO_DATABASE_URL", "sqlite://:memory:"),
        conn_max_age=int(os.environ.get("DJANGO_DATABASE_CONN_MAX_AGE", "60")),
    )
}

# Authentication

LOGIN_URL = "members:login"
AUTH_USER_MODEL = "members.User"

AUTHENTICATION_BACKENDS = ["loefsys.members.backends.LoefbijterGroupBackend"]

# from: https://docs.djangoproject.com/en/5.0/topics/auth/passwords/#using-argon2-with-django
PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation."
        "UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "loefsys.members.password_validators.CustomComplexityValidator"},
]

# Security

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
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS")

# Localization

# Source strings are written in English. Dutch is the default language for every
# visitor; English is only shown when a user picks it with the language switcher.

# Fixed rather than read from the environment: times are always shown in
# Amsterdam time.
TIME_ZONE = "Europe/Amsterdam"
LANGUAGE_CODE = "nl"
LANGUAGES = [("nl", _("Dutch")), ("en", _("English"))]
USE_I18N = True
USE_TZ = True

LOCALE_DIR = BASE_DIR / "locale"
LOCALE_PATHS = [LOCALE_DIR]

# Static files and media storage

AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")
AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
USES_LOCAL_STORAGE = DEBUG or not AWS_STORAGE_BUCKET_NAME

STATICFILES_FINDERS = [
    # Default finders
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    # Required by django-compressor's {% compress %} template tag.
    "compressor.finders.CompressorFinder",
]
STATICFILES_DIRS = [BASE_DIR / "static", BASE_DIR / "styles" / "dist"]

STATIC_URL = (
    "static/" if USES_LOCAL_STORAGE else f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
)
MEDIA_URL = "media/" if USES_LOCAL_STORAGE else f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
STATIC_ROOT = BASE_DIR / "collectedstatic"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "storages.backends.s3boto3.S3Boto3Storage"
        if AWS_STORAGE_BUCKET_NAME
        else "django.core.files.storage.FileSystemStorage"
    },
    "staticfiles": {
        "BACKEND": "storages.backends.s3boto3.S3StaticStorage"
        if AWS_STORAGE_BUCKET_NAME
        else "django.contrib.staticfiles.storage.StaticFilesStorage"
    },
}

# Tailwind

TAILWIND_APP_NAME = "loefsys.theme"
TAILWIND_VERSION = "v4.1.17"
TAILWIND_BIN_PATH = os.environ.get("TAILWIND_BIN_PATH")
TAILWIND_INPUT_CSS = BASE_DIR / "styles" / "globals.css"
NPM_BIN_PATH = os.environ.get("NPM_BIN_PATH", "npm")

# Email

EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND", "django.core.mail.backends.filebased.EmailBackend"
)
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"

EMAIL_HOST = os.environ.get("DJANGO_EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("DJANGO_EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("DJANGO_EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("DJANGO_EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("DJANGO_EMAIL_USE_TLS", True)

EMAIL_TIMEOUT = 5

DEFAULT_FROM_EMAIL = "Loefbijter <noreply@loefbijter.nl>"
EMAIL_SUBJECT_PREFIX = "[Loefbijter]"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Logging

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "filters": {"require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}},
    "formatters": {
        "verbose": {
            "format": "%(levelname)s %(asctime)s %(module)s "
            "%(process)d %(thread)d %(message)s"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler",
        },
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
    },
    "root": {"level": "INFO", "handlers": ["console"]},
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "django.security.DisallowedHost": {
            "level": "ERROR",
            "handlers": ["console", "mail_admins"],
            "propagate": True,
        },
    },
}

# Django Dynamic Fixture (tests)

DDF_IGNORE_FIELDS = ("display_name",)
DDF_FIELD_FIXTURES = {"django.db.models.fields.generated.GeneratedField": lambda: None}
