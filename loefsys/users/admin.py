"""Admin configuration for the User model."""

from typing import ClassVar

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext as _

from .models import Address, MemberDetails, Membership, StudyRegistration, User


class StudyRegistrationInline(admin.StackedInline):
    """Inline admin for the StudyRegistration model."""

    model = StudyRegistration
    extra = 0
    fields = ("institution", "programme", "student_number", "rsc_number")


# class AddressInlineForm(forms.ModelForm):
#     """Custom form for the Address inline."""

#     class Meta:
#         model = Address
#         fields = ("street", "street2", "postal_code", "city", "country")

#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#         if self.instance.pk and hasattr(self.instance, "memberdetails"):
#             try:
#                 self.instance = self.instance.memberdetails.address
#             except ObjectDoesNotExist:
#                 pass


# class AddressInline(admin.StackedInline):
#     """Custom inline admin for the Address model."""

#     model = Address
#     form = AddressInlineForm
#     extra = 0
#     fields = ("street", "street2", "postal_code", "city", "country")

#     def get_queryset(self, request):
#         """Filter the queryset to only show addresses linked to MemberDetails."""
#         qs = super().get_queryset(request)
#         return qs.filter(memberdetails__isnull=False)


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin class for the Address model."""

    list_display = ("street", "city", "postal_code", "country")
    search_fields = ("street", "city", "postal_code", "country")


class MembershipInline(admin.TabularInline):
    """Inline admin for the Membership model."""

    model = Membership
    extra = 0
    fields = ("membership_type", "start", "end")


@admin.register(MemberDetails)
class MemberDetailsAdmin(admin.ModelAdmin):
    """Admin class for the MemberDetails model."""

    inlines: ClassVar = [MembershipInline, StudyRegistrationInline]  # AddressInline]
    fields = ("gender", "birthday")


class MemberDetailsInline(admin.StackedInline):
    """Inline admin for the MemberDetails model."""

    model = MemberDetails
    extra = 1
    fields = ("gender", "birthday")
    inlines: ClassVar = [MembershipInline, StudyRegistrationInline]  # AddressInline]


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
