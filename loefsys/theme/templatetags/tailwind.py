"""Module containing template tags for the tailwind integration."""

import time

from django import template
from django.conf import settings
from django.templatetags.static import StaticNode

register = template.Library()


@register.simple_tag(name="tailwind")
def do_tailwind():
    """Retrieve the static url for the stylesheet.

    In debug mode, a url parameter is added to force refresh upon changes.
    """
    url = StaticNode.handle_simple("styles.css")
    if settings.DEBUG:
        url += f"?v={int(time.time())}"
    return url
