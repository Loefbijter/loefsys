"""Admin configuration for the Announcement model."""

from django.contrib import admin

from .models import Announcement, StaticPage


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    """Admin interface for managing announcements."""

    list_display = ("title", "published", "announcement_start", "announcement_end")
    list_filter = ("published",)
    search_fields = ("title", "content")
    ordering = ("-created_at",)
    fields = (
        "title",
        "content",
        "announcement_start",
        "announcement_end",
        "published",
        "created_at",
        "updated_at",
    )
    readonly_fields = ("created_at", "updated_at")


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    """Admin interface for managing static information pages."""

    list_display = ("title", "slug")
    search_fields = ("title", "content")
    ordering = ("title",)
    fields = ("title", "slug", "content", "created_at", "updated_at")
    readonly_fields = ("created_at", "updated_at")
