"""Admin configuration for the User model."""

from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from .models import Address, MemberDetails, Membership, StudyRegistration, User


class MembershipInline(admin.TabularInline):
    """Inline admin for the Membership model."""

    model = Membership
    extra = 0
    fields = ("membership_type", "start", "end")


class StudyRegistrationInline(admin.StackedInline):
    """Inline admin for the StudyRegistration model."""

    model = StudyRegistration
    extra = 0
    fields = ("institution", "programme", "student_number", "rsc_number")


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin class for the Address model."""

    list_display = ("street", "city", "postal_code", "country")
    search_fields = ("street", "city", "postal_code", "country")


@admin.register(MemberDetails)
class MemberDetailsAdmin(admin.ModelAdmin):
    """Admin class for the MemberDetails model."""

    inlines: ClassVar = [MembershipInline, StudyRegistrationInline]
    fields = ("user", "gender", "birthday", "show_birthday", "address")
    list_dislay = ("user", "gender", "birthday", "show_birthday", "address")
    search_fields = ("user__email", "user__first_name", "user__last_name")


class MemberDetailsInline(admin.StackedInline):
    """Inline admin for the MemberDetails model."""

    model = MemberDetails
    extra = 0
    fields = ("gender", "birthday", "show_birthday", "address")
    can_delete = False


class GuestUser(User):
    """Proxy model for GuestUser, inheriting from User."""

    class Meta:
        proxy = True
        verbose_name = _("Guest User")
        verbose_name_plural = _("Guest Users")


@admin.register(GuestUser)
class GuestUserAdmin(BaseUserAdmin):
    """Admin class for the GuestUser proxy model."""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "is_active",
                    "phone_number",
                    "note",
                )
            },
        ),
        (_("Permissions"), {"fields": ("is_staff", "is_superuser")}),
        (_("Groups"), {"fields": ("groups",)}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "phone_number", "note")},
        ),
        (_("Permissions"), {"fields": ("is_staff", "is_superuser")}),
        (_("Groups"), {"fields": ("groups",)}),
    )

    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)

    def get_queryset(self, request):
        """Return the queryset of users without MemberDetails."""
        qs = super().get_queryset(request)
        return qs.filter(member__isnull=True)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin class for the User model."""

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "first_name",
                    "last_name",
                    "is_active",
                    "phone_number",
                    "note",
                )
            },
        ),
        (_("Permissions"), {"fields": ("is_staff", "is_superuser")}),
        (_("Groups"), {"fields": ("groups",)}),
    )

    add_fieldsets = (
        (None, {"classes": ("wide",), "fields": ("email", "password1", "password2")}),
        (
            _("Personal info"),
            {"fields": ("first_name", "last_name", "phone_number", "note")},
        ),
        (_("Permissions"), {"fields": ("is_staff", "is_superuser")}),
        (_("Groups"), {"fields": ("groups",)}),
    )

    list_display = ("email", "first_name", "last_name", "is_staff")
    search_fields = ("email", "first_name", "last_name")
    ordering = ("email",)
    inlines: ClassVar = [MemberDetailsInline]

    def get_fieldsets(self, request, obj=None):
        """Return the fieldsets for the User model."""
        if not obj:
            return self.add_fieldsets
        return super().get_fieldsets(request, obj)
