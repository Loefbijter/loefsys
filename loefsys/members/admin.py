"""Admin configuration for the User model."""

from django.contrib import admin, messages
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.core.exceptions import PermissionDenied, ValidationError
from django.db.models import Exists, OuterRef, Subquery
from django.db.utils import OperationalError
from django.forms import BaseInlineFormSet, ModelMultipleChoiceField
from django.utils.translation import gettext_lazy as _

from loefsys.admin_helpers import ExportableModelAdmin
from loefsys.privacy import pseudonymize_users

from .models import Membership, Skippership, User, UserSkippership
from .models.choices import MembershipTypes
from .models.membership import validate_has_overlap
from .skipperships import backfill_required_skipperships


class UserSkippershipFormSet(BaseInlineFormSet):
    """Formset that lets a skippership and its required one be added together."""

    def add_fields(self, form, index):
        """Tell each row which skipperships the other rows are adding."""
        super().add_fields(form, index)
        form.instance.pending_skippership_ids = self._submitted_skippership_ids()

    def _submitted_skippership_ids(self) -> set[int]:
        """Return the skipperships selected in the submitted, non-deleted rows."""
        if not self.is_bound:
            return set()
        ids = set()
        for i in range(self.total_form_count()):
            prefix = f"{self.prefix}-{i}"
            value = self.data.get(f"{prefix}-skippership", "")
            if value.isdigit() and not self.data.get(f"{prefix}-DELETE"):
                ids.add(int(value))
        return ids


class UserSkippershipInline(admin.TabularInline):
    """Inline admin for assigning skipperships to a user."""

    model = UserSkippership
    formset = UserSkippershipFormSet
    extra = 1
    autocomplete_fields = ("skippership",)


class MembershipFormSet(BaseInlineFormSet):
    """Formset that checks the user's memberships don't overlap each other.

    The rows are checked against each other as submitted, so a membership can be
    ended and its follow-up added in the same save.
    """

    def add_fields(self, form, index):
        """Leave the overlap check of each row to the formset."""
        super().add_fields(form, index)
        form.instance.overlap_checked_by_formset = True

    def clean(self):
        """Raise an error when two of the kept rows overlap."""
        super().clean()
        checked: list[Membership] = []
        for form in self.forms:
            data = getattr(form, "cleaned_data", None)
            if not data or data.get("DELETE") or not data.get("start"):
                continue
            membership = Membership(
                pk=form.instance.pk, start=data["start"], end=data.get("end")
            )
            if validate_has_overlap(membership, checked):
                raise ValidationError(
                    _("Memberships can't overlap: one must end before the next starts.")
                )
            checked.append(membership)


class MembershipInline(admin.TabularInline):
    """Inline admin for a user's membership periods and their types."""

    model = Membership
    formset = MembershipFormSet
    extra = 0
    fields = ("membership_type", "start", "end")
    ordering = ("start",)


class SkippershipUserInline(admin.TabularInline):
    """Inline admin for viewing and assigning users to a skippership."""

    model = UserSkippership
    fk_name = "skippership"
    extra = 1
    autocomplete_fields = ("user",)


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


class CurrentMembershipFilter(admin.SimpleListFilter):
    """Filter users on the type of the membership that applies today."""

    title = _("current membership")
    parameter_name = "membership"

    def lookups(self, _request, _model_admin):
        """Return the membership types, and an option for no current membership."""
        return [
            *((str(value), label) for value, label in MembershipTypes.choices),
            ("none", _("No current membership")),
        ]

    def queryset(self, _request, queryset):
        """Return the users whose current membership matches the selected option."""
        match self.value():
            case None:
                return queryset
            case "none":
                return queryset.filter(current_membership_type__isnull=True)
            case value if value.isdigit():
                return queryset.filter(current_membership_type=int(value))
        return queryset


@admin.register(User)
class UserAdmin(ExportableModelAdmin, BaseUserAdmin):
    """Admin class for the User model."""

    inlines = (MembershipInline, UserSkippershipInline)

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
                allowed = user is not None and user.has_perm(perm)
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

    list_display = (
        "email",
        "first_name",
        "last_name",
        "current_membership_type",
        "has_admin_permission",
    )
    list_filter = (
        CurrentMembershipFilter,
        AdminPermissionFilter,
        "is_superuser",
        "is_active",
        "groups",
    )
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    filter_horizontal = ("groups", "user_permissions")

    @admin.display(
        description=_("Admin"), boolean=True, ordering="has_admin_permission"
    )
    def has_admin_permission(self, user):
        """Return whether the user was given the Admin permission directly."""
        return user.has_admin_permission

    @admin.display(description=_("Membership"), ordering="current_membership_type")
    def current_membership_type(self, user):
        """Return the type of the membership that applies today."""
        if user.current_membership_type is None:
            return None
        return MembershipTypes(user.current_membership_type).label

    def get_queryset(self, request):
        """Annotate the current membership and the Admin permission of each user."""
        return (
            super()
            .get_queryset(request)
            .annotate(
                current_membership_type=Subquery(
                    Membership.objects.current()
                    .filter(member=OuterRef("pk"))
                    .order_by("-start")
                    .values("membership_type")[:1]
                ),
                has_admin_permission=Exists(
                    User.user_permissions.through.objects.filter(
                        user=OuterRef("pk"),
                        permission__codename="access_admin",
                        permission__content_type__app_label="members",
                    )
                ),
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

    list_display = ("name", "parent")
    search_fields = ("name",)
    autocomplete_fields = ("parent",)
    inlines = (SkippershipUserInline,)

    def save_model(self, request, obj, form, change):
        """Give existing skippers the skipperships a new parent makes required."""
        super().save_model(request, obj, form, change)
        if obj.parent_id is not None and "parent" in form.changed_data:
            count = backfill_required_skipperships(Skippership, UserSkippership)
            if count:
                messages.info(
                    request,
                    _("Added %(count)d required skipperships to existing skippers.")
                    % {"count": count},
                )
