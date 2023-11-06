from django.contrib import admin
from django.utils import timezone
from django.db.models import Q

from .models import Committee, CommitteeMembership


class CommitteeInline(admin.TabularInline):
    model = CommitteeMembership
    verbose_name = "member"
    verbose_name_plural = "current members"
    extra = 0
    ordering = ("-is_head", "since")

    def get_queryset(self, request):
        return super(CommitteeInline, self).get_queryset(request).filter(Q(until__gte=timezone.now()) | Q(until=None))

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class CommitteeOldMembersInline(admin.TabularInline):
    model = CommitteeMembership
    verbose_name = "old member"
    verbose_name_plural = "old members"
    extra = 0
    ordering = ("-is_head", "member", "since")

    def get_queryset(self, request):
        return super(CommitteeOldMembersInline, self).get_queryset(request).filter(until__lt=timezone.now())

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request, obj=None):
        return False


class CommitteeAdmin(admin.ModelAdmin):
    inlines = [CommitteeInline, CommitteeOldMembersInline]


admin.site.register(Committee, CommitteeAdmin)
