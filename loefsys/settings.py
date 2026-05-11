import os
from pathlib import Path

from dotenv import load_dotenv
import dj_database_url

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("Environment variable DJANGO_SECRET_KEY must be set.")

DEBUG = os.environ.get("DJANGO_DEBUG", "False").lower() in ("true", "1", "t")

ALLOWED_HOSTS = os.environ.get("DJANGO_ALLOWED_HOSTS", "").split(",")
if ALLOWED_HOSTS == [""]:
    ALLOWED_HOSTS = []

# Application definition
INSTALLED_APPS = [
    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Third party apps
    "django_cotton",
    "django_browser_reload",
]

if DEBUG:
    INSTALLED_APPS.append("debug_toolbar")

INSTALLED_APPS += [
    # Local apps
    "loefsys.core",
    "loefsys.events",
    "loefsys.groups",
    # "loefsys.reservations",
    "loefsys.members",
    "loefsys.home",
    "loefsys.theme",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "loefsys.core.middleware.UserAgentMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

if DEBUG:
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")
    INTERNAL_IPS = ["127.0.0.1", "localhost"]
else:
    INTERNAL_IPS = []

ROOT_URLCONF = "loefsys.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.i18n",
                "django.template.context_processors.tz",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                "loefsys.core.context_processors.is_mobile",
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
DATABASES = {
    "default": dj_database_url.parse(
        os.environ.get("DJANGO_DATABASE_URL", "sqlite://:memory:"),
        conn_max_age=int(os.environ.get("DJANGO_DATABASE_CONN_MAX_AGE", "60"))
    )
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
    {"NAME": "loefsys.members.password_validators.CustomComplexityValidator"},
]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.Argon2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2PasswordHasher",
    "django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher",
    "django.contrib.auth.hashers.BCryptSHA256PasswordHasher",
    "django.contrib.auth.hashers.ScryptPasswordHasher",
]

AUTH_USER_MODEL = "members.User"
LOGIN_URL = "members:login"

# Internationalization
LANGUAGE_CODE = "nl-NL"
TIME_ZONE = os.environ.get("DJANGO_TIME_ZONE", "Europe/Amsterdam")
USE_I18N = True
USE_TZ = True

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

# Static files (CSS, JavaScript, Images)
AWS_STORAGE_BUCKET_NAME = os.environ.get("DJANGO_AWS_STORAGE_BUCKET_NAME")

STATIC_URL = "static/"
MEDIA_URL = "media/"
if AWS_STORAGE_BUCKET_NAME:
    AWS_S3_CUSTOM_DOMAIN = f"{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com"
    STATIC_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/static/"
    MEDIA_URL = f"https://{AWS_S3_CUSTOM_DOMAIN}/media/"

STATICFILES_DIRS = [
    BASE_DIR / "static",
    BASE_DIR / "styles" / "dist",
]

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

STATICFILES_FINDERS = (
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Tailwind Configuration
TAILWIND_APP_NAME = "loefsys.theme"
TAILWIND_VERSION = "v4.1.17"
TAILWIND_BIN_PATH = os.environ.get("TAILWIND_BIN_PATH", str(BASE_DIR / "tailwindcss"))
TAILWIND_INPUT_CSS = BASE_DIR / "styles" / "globals.css"

if os.name == 'nt':
    NPM_BIN_PATH = "npm.cmd"
else:
    NPM_BIN_PATH = "npm"

# Email Configuration
EMAIL_BACKEND = "django.core.mail.backends.filebased.EmailBackend"
EMAIL_FILE_PATH = BASE_DIR.parent / "sent_emails"
EMAIL_TIMEOUT = 5
DEFAULT_FROM_EMAIL = "Loefbijter <noreply@loefbijter.nl>"
SERVER_EMAIL = DEFAULT_FROM_EMAIL
EMAIL_SUBJECT_PREFIX = "[Loefbijter]"

# Test Settings
DDF_IGNORE_FIELDS = ("display_name",)
DDF_FIELD_FIXTURES = {
    "django.db.models.fields.generated.GeneratedField": lambda: None
}
