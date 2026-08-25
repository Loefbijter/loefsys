"""Module defining common middlewares."""

from urllib.parse import quote

from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.functional import SimpleLazyObject
from user_agent_parser import Parser

HTTP_NOT_FOUND = 404


class UserAgentMiddleware:
    """The UserAgentMiddleware adds user agent data to the request."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Add the user agent to the current request."""

        def get_user_agent():
            user_agent_string = request.META.get("HTTP_USER_AGENT", "")
            return Parser(user_agent_string)

        request.user_agent = SimpleLazyObject(get_user_agent)
        return self.get_response(request)


class ErrorPageMiddleware:
    """Render custom HTML error pages during development."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Render a custom 404 page for HTML responses."""
        response = self.get_response(request)

        if response.status_code == HTTP_NOT_FOUND and "text/html" in response.get(
            "Content-Type", ""
        ):
            return render(request, "404.html", status=HTTP_NOT_FOUND)

        return response


class RequireLoginMiddleware:
    """Ensure that users must be authenticated to access most pages.

    This middleware redirects anonymous users to the login page unless the
    request path is explicitly whitelisted (login/logout, admin, static/media,
    debug tools, and browser reload). Add additional exceptions here if needed.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Process the incoming request and enforce login/whitelist rules.

        If the user is authenticated, ensure sensitive pages are not cached.
        Otherwise redirect anonymous users to the login page when needed.
        """
        if getattr(request, "user", None) and request.user.is_authenticated:
            response = self.get_response(request)
            try:
                # Prevent browsers from caching authenticated pages.
                # This helps avoid briefly seeing content after logout via
                # back/forward navigation.
                if (
                    getattr(response, "has_header", lambda _: False)("Cache-Control")
                    is False
                ):
                    response["Cache-Control"] = "no-store"
                    response["Pragma"] = "no-cache"
            except Exception:
                # Be conservative: if headers cannot be set, just return response.
                pass
            return response

        # Whitelist paths that should remain publicly accessible.
        path = request.path
        # Common public endpoints that should not require authentication
        allowed_prefixes = [
            reverse("login"),
            "/logout/",
            "/members/logout/",
            "/members/reset-password/",  # Allow password reset request page
            "/reset/",  # Allow password reset pages (reset confirm and reset done)
            "/reset-disabled/",  # Allow reset disabled message page
            "/admin/",
            "/__reload__/",
            "/__debug__/",
            settings.STATIC_URL if hasattr(settings, "STATIC_URL") else "/static/",
            settings.MEDIA_URL if hasattr(settings, "MEDIA_URL") else "/media/",
            "/favicon.ico",
        ]

        # Ensure none of the allowed prefixes are None and strip empty strings
        allowed_prefixes = [p for p in allowed_prefixes if p]

        for prefix in allowed_prefixes:
            if path.startswith(prefix):
                return self.get_response(request)

        # Not authenticated and not whitelisted — redirect to login with next param.
        login_url = reverse("login")
        return redirect(f"{login_url}?next={quote(request.get_full_path())}")
