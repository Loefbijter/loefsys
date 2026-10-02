"""Admin configuration for the User model."""

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import PermissionDenied
from django.db.models import Exists, OuterRef
from django.db.utils import OperationalError
from django.forms import ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from loefsys.admin_helpers import ExportableModelAdmin
from loefsys.privacy import pseudonymize_users

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


class AdminPermissionFilter(admin.SimpleListFilter):
    """Filter users on whether they were given the Admin permission directly.

    Everyone who had the old staff flag got this permission, so this lists them
    in one place to move them into the right groups.
    """

    title = _("Admin permission")
    parameter_name = "admin_permission"

    def lookups(self, _request, _model_admin):
        """Return the filter options."""
        return [("yes", _("Yes")), ("no", _("No"))]

    def queryset(self, _request, queryset):
        """Return the users matching the selected option."""
        match self.value():
            case "yes":
                return queryset.filter(has_admin_permission=True)
            case "no":
                return queryset.filter(has_admin_permission=False)
        return queryset


@admin.register(User)
class UserAdmin(ExportableModelAdmin, BaseUserAdmin):
    """Admin class for the User model."""

    inlines = (UserSkippershipInline,)

    actions = (*getattr(BaseUserAdmin, "actions", ()), "pseudonymize_selected")

    @admin.action(description=_("Pseudonymize selected users"))
    def pseudonymize_selected(self, request, queryset):
        """Admin action to pseudonymize selected users (AVG-compliant deletion).

        Only allow superusers or users with explicit permission.
        """
        # permission: require superuser or 'members.pseudonymize_user' permission
        user = getattr(request, "user", None)
        allowed = False
        if user and getattr(user, "is_superuser", False):
            allowed = True
        else:
            app = self.model._meta.app_label
            model_name = self.model._meta.model_name
            perm = f"{app}.pseudonymize_{model_name}"
            try:
                allowed = user.has_perm(perm)
            except Exception:
                allowed = False

        if not allowed:
            raise PermissionDenied

        count = pseudonymize_users(queryset)
        messages.success(request, _("%d users pseudonymized") % count)

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
        (_("Permissions"), {"fields": ("is_superuser", "user_permissions")}),
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
        (_("Permissions"), {"fields": ("is_superuser",)}),
        (_("Groups"), {"fields": ("groups",)}),
    )

    list_display = ("email", "first_name", "last_name", "has_admin_permission")
    list_filter = (AdminPermissionFilter, "is_superuser", "is_active", "groups")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")

    @admin.display(
        description=_("Admin"), boolean=True, ordering="has_admin_permission"
    )
    def has_admin_permission(self, user):
        """Return whether the user was given the Admin permission directly."""
        return user.has_admin_permission

    def get_queryset(self, request):
        """Annotate whether each user holds the Admin permission directly."""
        return (
            super()
            .get_queryset(request)
            .annotate(
                has_admin_permission=Exists(
                    User.user_permissions.through.objects.filter(
                        user=OuterRef("pk"),
                        permission__codename="access_admin",
                        permission__content_type__app_label="members",
                    )
                )
            )
        )

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
class SkippershipAdmin(ExportableModelAdmin):
    """Admin class for the Skippership model."""

    list_display = ("name",)
    search_fields = ("name",)
    inlines = (SkippershipUserInline,)
