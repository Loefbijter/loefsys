"""Settings for the theme module."""

from pathlib import Path

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

DEFAULTS = {
    "TAILWIND_VERSION": "latest",
    "TAILWIND_BIN_PATH": None,
    "TAILWIND_OUTPUT_CSS": None,
}


def _import_from_settings(setting):
    try:
        if setting in DEFAULTS:
            return getattr(settings, setting, DEFAULTS[setting])
        return getattr(settings, setting)
    except AttributeError:
        raise ImproperlyConfigured(f"Setting {setting} not found.")


TAILWIND_VERSION = _import_from_settings("TAILWIND_VERSION")
TAILWIND_BIN_PATH = _import_from_settings("TAILWIND_BIN_PATH")
TAILWIND_INPUT_CSS = Path(_import_from_settings("TAILWIND_INPUT_CSS"))
TAILWIND_OUTPUT_CSS = Path(
    _import_from_settings("TAILWIND_OUTPUT_CSS")
    or TAILWIND_INPUT_CSS.parent / "dist" / TAILWIND_INPUT_CSS.name
)
