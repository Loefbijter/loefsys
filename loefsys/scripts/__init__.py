"""A collection of scripts to manage the dev environment."""

from .code_scripts import format, lint, typecheck
from .django_scripts import (
    collectstatic,
    createsuperuser,
    makemigrations,
    migrate,
    runserver,
    test,
)
from .sphinx_scripts import genapidocs, makedocs

__all__ = [
    "collectstatic",
    "createsuperuser",
    "format",
    "genapidocs",
    "lint",
    "makedocs",
    "makemigrations",
    "migrate",
    "runserver",
    "test",
    "typecheck",
]
