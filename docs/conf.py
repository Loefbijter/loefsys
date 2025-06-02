"""Configuration file for the Sphinx documentation builder.

For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html
"""

import os
import sys
from pathlib import Path

import django

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = "Loefsys"
copyright = "2024, Loefbijter Webcie"  # noqa: A001
author = "Loefbijter Webcie"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

sys.path.insert(1, str(Path(__file__).parent / "_ext"))
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.intersphinx",
    "sphinx.ext.napoleon",
    "celery.contrib.sphinx",
    "sphinxcontrib.mermaid",
    "djangodocs",
    "ref_aliases",
]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

nitpicky = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]

# -- Options for Intersphinx -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html

intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
    "django": (
        "https://docs.djangoproject.com/en/5.0/",
        "https://docs.djangoproject.com/en/5.0/_objects/",
    ),
    "django_ext": ("https://django-extensions.readthedocs.io/en/latest/", None),
    "django_cbs": ("https://django-classy-settings.readthedocs.io/latest/", None),
    "sphinx": ("https://www.sphinx-doc.org/en/master/", None),
    "mypy": ("https://mypy.readthedocs.io/en/latest/", None),
}
intersphinx_disabled_reftypes = []

# -- Options for Autodoc -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/autodoc.html

autodoc_typehints = "both"
autodoc_member_order = "bysource"
autodoc_type_aliases = {"EventRegistration": "~loefsys.events.models.EventRegistration"}

# -- Options for Napoleon ----------------------------------------------------

napoleon_preprocess_types = False

# -- Options for Django configuration ----------------------------------------

sys.path.insert(0, str(Path(__file__).resolve(strict=True).parent.parent))
os.environ["DJANGO_SETTINGS_MODULE"] = "loefsys.settings"
django.setup()

alias_mapping = {
    "django.db.models.base.Model": (None, "django.db.models.Model"),
    "django.apps.config.AppConfig": (None, "django.apps.AppConfig"),
    "django.db.models.enums.IntegerChoices": (None, "django.db.models.Field"),
    "django.db.models.manager.Manager": (None, "django.db.models.Manager"),
    "django.contrib.auth.base_user.BaseUserManager": (
        None,
        "django.contrib.auth.models.BaseUserManager",
    ),
    "django.contrib.auth.base_user.AbstractBaseUser": (
        None,
        "django.contrib.auth.models.AbstractBaseUser",
    ),
    "django_extensions.db.models.TimeStampedModel": ("std:doc", "model_extensions"),
    "django_extensions.db.models.TitleSlugDescriptionModel": (
        "std:doc",
        "model_extensions",
    ),
}
