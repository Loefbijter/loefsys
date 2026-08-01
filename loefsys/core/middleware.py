"""Module defining common middlewares."""

from django.http import HttpRequest
from django.shortcuts import render
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
