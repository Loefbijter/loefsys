"""Module containing template tags for the tailwind integration."""

import time

from django import template
from django.conf import settings
from django.http import QueryDict

register = template.Library()


@register.inclusion_tag("theme/tailwind_url.html", name="tailwind_static_url")
def do_tailwind():
    """Retrieve the static url for the stylesheet.

    In debug mode, a url parameter is added to force refresh upon changes.
    """
    qd = QueryDict(mutable=True)
    if settings.DEBUG:
        qd["v"] = str(int(time.time()))
    return {"url": "styles.css", "qd": qd}
