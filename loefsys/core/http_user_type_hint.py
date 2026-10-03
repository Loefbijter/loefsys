"""Typing helpers for HTTP requests."""

from django.http import HttpRequest

from loefsys.members.models import User


class AuthenticatedHttpRequest(HttpRequest):
    """An ``HttpRequest`` whose user is known to be logged in.

    Only used for type annotations on views guarded by ``LoginRequiredMixin``.
    """

    user: User
