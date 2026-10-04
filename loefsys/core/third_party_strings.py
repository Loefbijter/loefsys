"""Strings from third-party packages that ship no Dutch translation.

Listing them here makes ``makemessages`` pick them up, so that their Dutch
translation lives in our own catalogue. The fields come from django-extensions'
``TimeStampedModel`` and ``TitleSlugDescriptionModel``, which several of our
models use.
"""

from django.utils.translation import gettext_noop

STRINGS = (
    gettext_noop("created"),
    gettext_noop("modified"),
    gettext_noop("title"),
    gettext_noop("description"),
    gettext_noop("slug"),
)
