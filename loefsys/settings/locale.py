"""Module containing the configuration for the localization."""

from collections.abc import Sequence
from pathlib import Path
from typing import cast

from django.utils.translation import gettext_lazy as _

from .auth import AuthSettings
from .base import BaseSettings
from .templates import TemplateSettings


class LocaleSettings(AuthSettings, TemplateSettings, BaseSettings):
    """Class containing the configuration for the localization.

    Source strings are written in English. Dutch is the default language for every
    visitor; English is only shown when a user picks it with the language switcher.
    """

    # Fixed rather than read from the environment: times are always shown in
    # Amsterdam time.
    TIME_ZONE = "Europe/Amsterdam"
    LANGUAGE_CODE = "nl"
    LANGUAGES = (("nl", _("Dutch")), ("en", _("English")))
    USE_I18N = True
    USE_TZ = True

    def LOCALE_DIR(self) -> Path:  # noqa N802 D102
        return self.BASE_DIR / "locale"

    def LOCALE_PATHS(self) -> Sequence[Path]:  # noqa N802 D102
        return (cast(Path, self.LOCALE_DIR),)

    def MIDDLEWARE(self) -> Sequence[str]:  # noqa N802 D102
        # Activate the language before any middleware that may render or redirect.
        middleware = list(super().MIDDLEWARE())
        session = "django.contrib.sessions.middleware.SessionMiddleware"
        index = middleware.index(session) + 1 if session in middleware else 0
        middleware.insert(index, "loefsys.core.i18n.LanguageMiddleware")
        return tuple(middleware)

    def templates_context_processors(self) -> Sequence[str]:  # noqa D102
        return (
            *super().templates_context_processors(),
            "django.template.context_processors.i18n",
            "django.template.context_processors.tz",
        )
