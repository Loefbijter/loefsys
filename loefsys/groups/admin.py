"""Module defining the admin panel for groups."""

from django.contrib import admin
from django.db.models.functions import Now
from django.utils.translation import gettext_lazy as _

from loefsys.admin_helpers import ExportableModelAdmin

from .models import Board, Committee, Fraternity, Taskforce, YearClub
from .models.membership import GroupMembership


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
                return queryset.filter(date_discontinuation=None) | queryset.filter(
                    date_discontinuation__gte=Now()
                )
            case "inactive":
                return queryset.filter(date_discontinuation__lt=Now())


class GroupUserInline(admin.TabularInline):
    """Inline to add/remove users for a group via the GroupMembership model."""

    model = GroupMembership
    fk_name = "group"
    extra = 1
    autocomplete_fields = ("user",)


@admin.register(Board)
class BoardAdmin(ExportableModelAdmin):
    """Admin interface for the board model."""

    inlines = (GroupUserInline,)
    list_display = ("name", "year")
    list_filter = (GroupActivityFilter,)
    search_fields = ("name", "description", "year")
    filter_horizontal = ("permissions",)


@admin.register(Committee)
class CommitteeAdmin(ExportableModelAdmin):
    """Admin interface for the committee model."""

    inlines = (GroupUserInline,)
    list_display = ("name", "description")
    list_filter = ("mandatory", GroupActivityFilter)
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)


@admin.register(Fraternity)
class FraternityAdmin(ExportableModelAdmin):
    """Admin interface for the fraternity model."""

    inlines = (GroupUserInline,)
    list_display = ("name", "gender_base")
    list_filter = (GroupActivityFilter,)
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)


@admin.register(Taskforce)
class TaskforceAdmin(ExportableModelAdmin):
    """Admin interface for the taskforce model."""

    inlines = (GroupUserInline,)
    list_display = ("name", "description", "requires_nda")
    list_filter = (GroupActivityFilter, "requires_nda")
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)


@admin.register(YearClub)
class YearClubAdmin(ExportableModelAdmin):
    """Admin interface for the year club model."""

    inlines = (GroupUserInline,)
    list_display = ("name", "year")
    list_filter = (GroupActivityFilter,)
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)
