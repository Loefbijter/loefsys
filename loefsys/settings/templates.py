"""Module containing the configuration for templates."""

from collections.abc import Sequence


class TemplateSettings:
    """Class containing the configuration for templates."""

    FORM_RENDERER = "django.forms.renderers.TemplatesSetting"

    def TEMPLATES(self) -> Sequence[dict]:  # noqa N802 D102
        return (
            {
                "BACKEND": "django.template.backends.django.DjangoTemplates",
                "DIRS": [self.BASE_DIR / "templates"],
                "APP_DIRS": True,
                "OPTIONS": {
                    "context_processors": self.templates_context_processors(),
                    "loaders": self.templates_loaders(),
                },
            },
        )

    def templates_context_processors(self) -> Sequence[str]:  # noqa D102
        return (
            "django.template.context_processors.debug",
            "django.template.context_processors.request",
            "loefsys.core.context_processors.is_mobile",
        )

    def templates_loaders(self):  # noqa D102
        return [
            (
                "django.template.loaders.cached.Loader",
                [
                    # Default Django loader
                    "django.template.loaders.filesystem.Loader",
                    # Including this is the same as APP_DIRS=True
                    "django.template.loaders.app_directories.Loader",
                ],
            )
        ]
