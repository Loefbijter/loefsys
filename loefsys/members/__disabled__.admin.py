from django.contrib import admin

from .models.skippership import Skippership
from .models.user_skippership import UserSkippership


@admin.register(Skippership, UserSkippership)
class SkippershipAdmin(admin.ModelAdmin):
    """Admin class for the Skippership models."""
