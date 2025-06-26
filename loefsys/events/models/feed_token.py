"""Model for personalized iCal feed tokens."""

from django.db import models
from django.utils.crypto import get_random_string

from loefsys.members.models import User


class FeedToken(models.Model):
    """Used to personalize the ical Feed."""

    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    token = models.CharField(max_length=32, editable=False)

    def save(self, **kwargs):  # noqa: D102
        self.token = get_random_string(32)
        super().save(**kwargs)

    @staticmethod
    def get_user(token):  # noqa: D102
        try:
            return FeedToken.objects.get(token=token).user
        except FeedToken.DoesNotExist:
            return None

    def __str__(self):  # noqa: DJ012
        return f"FeedToken(user={self.user}, token={self.token})"
