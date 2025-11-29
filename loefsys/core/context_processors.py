"""Additional context processors for templates."""

from typing import Literal

from django.http import HttpRequest


def is_mobile(request: HttpRequest) -> dict[Literal["is_mobile"], bool]:
    """Add a user agent flag to the template context."""
    return {"is_mobile": request.user_agent.device_type == "Mobile"}
