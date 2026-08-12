"""Admin configuration for the User model."""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.db.utils import OperationalError
from django.forms import ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from .models import Skippership, User, UserSkippership


class UserSkippershipInline(admin.TabularInline):
    """Inline admin for assigning skipperships to a user."""

    model = UserSkippership
    extra = 1
    autocomplete_fields = ("skippership", "given_by")


class SkippershipUserInline(admin.TabularInline):
    """Inline admin for viewing and assigning users to a skippership."""

    model = UserSkippership
    fk_name = "skippership"
    extra = 1
    autocomplete_fields = ("user", "given_by")


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin class for the User model."""

    inlines = (UserSkippershipInline,)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "lichting",
                    "title",
                    "is_active",
                    "phone_number",
                    "pod_kb_link",
                    "pod_zb_link",
                    "picture",
                    "note",
                )
            },
        ),
        (_("Permissions"), {"fields": ("is_staff", "is_superuser")}),
        (_("Groups"), {"fields": ("groups", "loefbijter_groups")}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "lichting",
                    "title",
                    "phone_number",
                    "pod_kb_link",
                    "pod_zb_link",
                    "note",
                )
            },
        ),
        (_("Permissions"), {"fields": ("is_staff", "is_superuser")}),
        (_("Groups"), {"fields": ("groups",)}),
    )

    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ("groups",)

    def get_fieldsets(self, request, obj=None):
        """Return the fieldsets for the User model."""
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        """Provide a DB-error-safe form field for the loefbijter_groups M2M.

        In environments where migrations haven't been applied (missing M2M table)
        the default admin widget raises OperationalError. Catch that and provide
        a disabled empty field instead so the admin page can still render.
        """
        # Only special-case the loefbijter_groups field
        if db_field.name == "loefbijter_groups":
            try:
                return super().formfield_for_manytomany(db_field, request, **kwargs)
            except OperationalError:
                # Fall back to an empty, disabled field so the admin page doesn't crash.
                kwargs["queryset"] = db_field.remote_field.model.objects.none()
                field = ModelMultipleChoiceField(**kwargs)
                field.disabled = True
                return field

        return super().formfield_for_manytomany(db_field, request, **kwargs)


@admin.register(Skippership)
class SkippershipAdmin(admin.ModelAdmin):
    """Admin class for the Skippership model."""

    list_display = ("name",)
    search_fields = ("name",)
    inlines = (SkippershipUserInline,)
