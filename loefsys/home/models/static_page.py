"""Model for static information pages."""

from typing import ClassVar

from django.db import models


class StaticPage(models.Model):
    """Model for storing static organization information pages."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Metadata for the StaticPage model."""

        ordering: ClassVar[list[str]] = ["title"]

    def __str__(self):
        """Return the title of the page."""
        return self.title
