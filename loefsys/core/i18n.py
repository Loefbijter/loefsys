"""Module defining the language selection for requests."""

from django.conf import settings
from django.http import HttpRequest
from django.utils import translation
from django.utils.cache import patch_vary_headers


class LanguageMiddleware:
    """Activate the user's chosen language, defaulting to ``LANGUAGE_CODE``.

    Unlike Django's ``LocaleMiddleware``, the browser's ``Accept-Language`` header is
    ignored, so every visitor sees Dutch until they pick another language with the
    ``set_language`` view, which stores the choice in the language cookie.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest):
        """Activate the language for this request and mark the response with it."""
        language = get_language_from_cookie(request)
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()

        response = self.get_response(request)

        patch_vary_headers(response, ("Cookie",))
        response.headers.setdefault("Content-Language", language)
        return response


def get_language_from_cookie(request: HttpRequest) -> str:
    """Return the supported language from the language cookie, or the default."""
    cookie = request.COOKIES.get(settings.LANGUAGE_COOKIE_NAME)
    if cookie:
        try:
            return translation.get_supported_language_variant(cookie)
        except LookupError:
            pass
    return settings.LANGUAGE_CODE
