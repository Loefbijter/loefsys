"""Module defining common middlewares."""

from django.http import HttpRequest
from django.utils.functional import SimpleLazyObject
from user_agent_parser import Parser


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
