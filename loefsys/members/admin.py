from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from django.db.models import Q

from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .models import Member
from ..committees.models import CommitteeMembership
from ..groups.models import MemberGroupMembership


# from events.models import EventRegistration


class MemberInline(admin.StackedInline):
    model = Member
    verbose_name = "Membership"
    can_delete = False
    classes = ["collapse"]

    fieldsets = [
        (
            "Personal details",
            {
                "fields": [
                    "first_name",
                    "last_name",
                    "gender",
                    "birthday",
                    "student_number",
                    "institution",
                    "programme",
                ]
            },
        ),
        (
            "Contact details",
            {
                "fields": [
                    "phone_number",
                    "address_street",
                    "address_street2",
                    "address_postal_code",
                    "address_city",
                    "address_country",
                ]
            },
        ),
        (
            "Membership details",
            {
                "fields": [
                    "relation_number",
                    "remark",
                    "RSC_number",
                    "member_since",
                    "member_until",
                    "alumni_since",
                    "payment_method",
                    "IBAN",
                ]
            },
        ),
        (
            "Profile",
            {
                "fields": [
                    "initials",
                    "nickname",
                    "display_name_preference",
                    "show_birthday",
                ]
            },
        ),
    ]

    def get_queryset(self, request):
        return super(MemberInline, self).get_queryset(request)


class GroupsInline(admin.TabularInline):
    model = MemberGroupMembership
    extra = 0
    classes = ["collapse"]
    can_delete = False
    ordering = ("chair", "since")

    def get_queryset(self, request):
        return super(GroupsInline, self).get_queryset(request).filter(until=None)

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# class FutureEventRegistrationsInline(admin.TabularInline):
#     model = EventRegistration
#     extra = 0
#     classes = ["collapse"]
#     ordering = ["event"]
#
#     def get_queryset(self, request):
#         return (
#             super(FutureEventRegistrationsInline, self)
#             .get_queryset(request)
#             .filter(Q(event__end__gt=timezone.now()) & Q(date_cancelled=None))
#         )


class CommitteeHeadFilter(admin.SimpleListFilter):
    title = _("committee head")
    parameter_name = "is_head"

    def lookups(self, request, model_admin):
        return (
            ("Yes", _("Yes")),
            ("No", _("No")),
        )

    def queryset(self, request, queryset):
        committee_heads = CommitteeMembership.objects.filter(
            Q(is_head=True) & Q(until=None)
        ).values_list("user_id", flat=True)
        if self.value() == "Yes":
            return queryset.filter(id__in=committee_heads)

        if self.value() == "No":
            return queryset.exclude(id__in=committee_heads)


# class CityListFilter(admin.SimpleListFilter):
#     title = _("city")
#     parameter_name = "address_city"
#
#     def lookups(self, request, model_admin):
#         return (
#             ("Nijmegen", _("Nijmegen")),
#             ("Arnhem", _("Arnhem")),
#             ("Other", _("Other")),
#         )
#
#     def queryset(self, request, queryset):
#         if self.value() == "Nijmegen":
#             return queryset.filter(member__address_city__icontains="Nijmegen")
#
#         if self.value() == "Arnhem":
#             return queryset.filter(member__address_city__icontains="Arnhem")
#
#         if self.value() == "Other":
#             return queryset.exclude(
#                 Q(address_city__icontains="Arnhem")
#                 | Q(address_city__icontains="Nijmegen")
#             )


# class UserAdmin(DjangoUserAdmin):
#     # form = forms.UserChangeForm
#     # add_form = forms.UserCreationForm
#     list_display = [
#         "username",
#         "get_full_name",
#         "email",
#     ]  # , 'member__student_number', 'member__is_committee_head'
#     # actions = []
#     # inlines = [MemberInline, GroupsInline, FutureEventRegistrationsInline]
#     inlines = [MemberInline]
#     list_filter = (
#         # CommitteeHeadFilter,
#         "member__gender",
#         # CityListFilter,
#         # "groups",
#         "is_superuser",
#     )

class MemberAdmin(admin.ModelAdmin):
    inlines = [MemberInline, GroupsInline]


admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), MemberAdmin)
