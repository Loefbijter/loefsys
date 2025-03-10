"""Module defining the admin panel for groups."""

from django.contrib import admin
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _

from .models import Board, Committee, Fraternity, Taskforce, YearClub


class GroupActivityFilter(admin.SimpleListFilter):
    """Describes a filter that filters a queryset by a group's activity."""

    title = _("Activity Status")
    parameter_name = "activitystatus"

    def lookups(self, _request, _model_admin):
        """Return a list of filter options."""
        return [("active", _("Active")), ("inactive", _("Inactive"))]

    def queryset(self, _request, queryset):
        """Return the filtered queryset."""
        match self.value():
            case "active":
                return (
                queryset.filter(date_discontinuation = None)
                | queryset.filter(date_discontinuation__gte=Now())
            )
            case "inactive":
                return queryset.filter(date_discontinuation__lt=Now())


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    """Admin interface for the board model."""

    list_display = ("name", "year")
    list_filter = (GroupActivityFilter,)
    search_fields = ("name", "description", "year")
    filter_horizontal = ("permissions",)


@admin.register(Committee)
class CommitteeAdmin(admin.ModelAdmin):
    """Admin interface for the committee model."""

    list_display = ("name", "description")
    list_filter = ("mandatory", GroupActivityFilter)
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)


@admin.register(Fraternity)
class FraternityAdmin(admin.ModelAdmin):
    """Admin interface for the fraternity model."""

    list_display = ("name", "gender_base")
    list_filter = (GroupActivityFilter,)
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)


@admin.register(Taskforce)
class TaskforceAdmin(admin.ModelAdmin):
    """Admin interface for the taskforce model."""

    list_display = ("name", "description", "requires_nda")
    list_filter = (GroupActivityFilter, "requires_nda")
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)


@admin.register(YearClub)
class YearClubAdmin(admin.ModelAdmin):
    """Admin interface for the year club model."""

    list_display = ("name", "year")
    list_filter = (GroupActivityFilter,)
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)
