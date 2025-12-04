"""Module containing template tags for the tailwind integration."""

import time

from django import template
from django.conf import settings

register = template.Library()


@register.inclusion_tag("theme/tailwind.html", name="tailwind_static")
def do_tailwind(url):
    """Retrieve the static url for the stylesheet.

    In debug mode, a url parameter is added to force refresh upon changes.
    """
    qs = "" if not settings.DEBUG else f"?v={int(time.time())}"
    return {"url": url, "qs": qs}
