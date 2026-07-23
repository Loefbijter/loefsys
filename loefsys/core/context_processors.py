"""Additional context processors for templates."""

from typing import Literal

from django.http import HttpRequest

from loefsys.home.models import StaticPage


def is_mobile(request: HttpRequest) -> dict[Literal["is_mobile"], bool]:
    """Add a user agent flag to the template context."""
    return {"is_mobile": request.user_agent.device_type == "Mobile"}


def static_pages(_request: HttpRequest) -> dict:
    """Add static information pages to the template context."""
    return {"static_pages": StaticPage.objects.all().order_by("title")}
