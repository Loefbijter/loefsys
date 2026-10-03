"""Additional context processors for templates."""

from typing import Literal

from django.http import HttpRequest

from loefsys.home.models import StaticPage


def is_mobile(request: HttpRequest) -> dict[Literal["is_mobile"], bool]:
    """Add a user agent flag to the template context.

    ``request.user_agent`` is set by ``UserAgentMiddleware``, which does not run for
    requests handled outside the normal middleware chain -- notably static/media
    files served directly by Django (e.g. ``runserver --insecure`` with
    ``DEBUG=False``). Without the fallback, a missing static file's 404 handling
    would itself crash here while rendering the 404 page's context, turning it into
    an unhandled 500.
    """
    user_agent = getattr(request, "user_agent", None)
    return {"is_mobile": bool(user_agent) and user_agent.device_type == "Mobile"}


def static_pages(_request: HttpRequest) -> dict:
    """Add static information pages to the template context."""
    return {"static_pages": StaticPage.objects.all().order_by("title")}
