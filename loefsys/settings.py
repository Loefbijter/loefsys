"""
Django settings for loefsys project.
Consolidated from the loefsys/settings/ package structure.
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import dj_database_url

# Load .env file at the very beginning
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/

DEBUG = os.environ.get("DJANGO_DEBUG", "0") in ("1", "True", "true")

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Environment variable DJANGO_SECRET_KEY must be set.")

ALLOWED_HOSTS = [
    host.strip() for host in os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",") if host.strip()
]

# Application definition

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "django_cotton",
    "django_browser_reload",
    "compressor",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

INSTALLED_APPS += [
    "loefsys.core",
    "loefsys.events",
    "loefsys.groups",
    "loefsys.members",
    "loefsys.home",
    "loefsys.theme",
]

MIDDLEWARE = [
    "loefsys.core.middleware.UserAgentMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

if DEBUG:
    MIDDLEWARE.append("debug_toolbar.middleware.DebugToolbarMiddleware")

MIDDLEWARE += [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
]

ROOT_URLCONF = "loefsys.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "loefsys.core.context_processors.is_mobile",
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
    },
]

WSGI_APPLICATION = "loefsys.wsgi.application"

# Database
# https://docs.djangoproject.com/en/5.2/ref/settings/#databases

DATABASE_URL = os.environ.get("DJANGO_DATABASE_URL", "sqlite://:memory:")
CONN_MAX_AGE = int(os.environ.get("DJANGO_DATABASE_CONN_MAX_AGE", 60))

DATABASES = {
    "default": dj_database_url.parse(DATABASE_URL, conn_max_age=CONN_MAX_AGE)
}

# Password validation
# https://docs.djangoproject.com/en/5.2/ref/settings/#auth-password-validators

LOGIN_URL = "members:login"
AUTH_USER_MODEL = "members.User"

PASSWORD_HASHERS = (
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
)

AUTH_PASSWORD_VALIDATORS = (
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"
    },
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "loefsys.members.password_validators.CustomComplexityValidator"},
)

# Internationalization
# https://docs.djangoproject.com/en/5.2/topics/i18n/

TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Europe/Amsterdam")
LANGUAGE_CODE = "nl-NL"
USE_I18N = True
USE_TZ = True

LOCALE_DIR = BASE_DIR / "locale"
LOCALE_PATHS = (LOCALE_DIR,)

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.2/howto/static-files/

AWS_STORAGE_BUCKET_NAME = os.environ.get("AWS_STORAGE_BUCKET_NAME")

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

STATICFILES_DIRS = (
    BASE_DIR / "static",
    BASE_DIR / "styles" / "dist",
)

USES_LOCAL_STORAGE = DEBUG or not AWS_STORAGE_BUCKET_NAME

if AWS_STORAGE_BUCKET_NAME:
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"
else:
    STATIC_URL = "static/"
    MEDIA_URL = "media/"

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

# Default primary key field type
# https://docs.djangoproject.com/en/5.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Tailwind Integration

TAILWIND_APP_NAME = "loefsys.theme"
TAILWIND_VERSION = "v4.1.17"
TAILWIND_BIN_PATH = os.environ.get("TAILWIND_BIN_PATH")
TAILWIND_INPUT_CSS = BASE_DIR / "styles" / "globals.css"

NPM_BIN_PATH = os.environ.get("NPM_BIN_PATH", "npm")
INTERNAL_IPS = ["localhost", "127.0.0.1"] if DEBUG else []

# Email Settings

EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR / "sent_emails"
EMAIL_TIMEOUT = 5

DEFAULT_FROM_EMAIL = "Loefbijter <noreply@loefbijter.nl>"
EMAIL_SUBJECT_PREFIX = "[Loefbijter]"
SERVER_EMAIL = DEFAULT_FROM_EMAIL

# Django Dynamic Fixture settings (for tests)

DDF_IGNORE_FIELDS = ("display_name",)
DDF_FIELD_FIXTURES = {
    "django.db.models.fields.generated.GeneratedField": lambda: None
}

# Form rendering

FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

# ==============================================================================
# Comments from disabled settings modules
# ==============================================================================

# Security Settings (SecuritySettings was disabled in classy config)
# SESSION_COOKIE_HTTPONLY = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_HTTPONLY = True
# CSRF_COOKIE_SECURE = True
# SECURE_HSTS_SECONDS = 60
# SECURE_HSTS_INCLUDE_SUBDOMAINS = True
# SECURE_HSTS_PRELOAD = True
# SECURE_CONTENT_TYPE_NOSNIFF = True

# Logging Settings (LoggingSettings was disabled in classy config)
# LOGGING = {
#     "version": 1,
#     "disable_existing_loggers": False,
#     "filters": {
#         "require_debug_false": {"()": "django.utils.log.RequireDebugFalse"}
#     },
#     "formatters": {
#         "verbose": {
#             "format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"
#         }
#     },
#     "handlers": {
#         "mail_admins": {
#             "level": "ERROR",
#             "filters": ["require_debug_false"],
#             "class": "django.utils.log.AdminEmailHandler",
#         },
#         "console": {
#             "level": "DEBUG",
#             "class": "logging.StreamHandler",
#             "formatter": "verbose",
#         },
#     },
#     "root": {"level": "INFO", "handlers": ["console"]},
#     "loggers": {
#         "django.request": {
#             "handlers": ["mail_admins"],
#             "level": "ERROR",
#             "propagate": True,
#         },
#         "django.security.DisallowedHost": {
#             "level": "ERROR",
#             "handlers": ["console", "mail_admins"],
#             "propagate": True,
#         },
#     },
# }
