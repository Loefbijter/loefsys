"""Models for announcements displayed on the index page."""

from django.db import models
from django.utils.translation import gettext_lazy as _


class Announcement(models.Model):
    """Model representing an announcement on the index page."""

    title = models.CharField(max_length=32, verbose_name=_("Title"))
    content = models.TextField(max_length=200, verbose_name=_("Content"))
    announcement_start = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Announcement start")
    )
    announcement_end = models.DateTimeField(
        null=True, blank=True, verbose_name=_("Announcement end")
    )
    published = models.BooleanField(default=False, verbose_name=_("Published"))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    def __str__(self):
        return self.title
