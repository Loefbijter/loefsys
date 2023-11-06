from django.contrib import admin

from .models import Fraternity, Board, YearClub, MemberGroupMembership


class MemberGroupMembershipInline(admin.TabularInline):
    model = MemberGroupMembership
    verbose_name = "membership"
    verbose_name_plural = "memberships"
    extra = 0

    # def get_queryset(self, request):
    #     return super(FraternityInline, self).get_queryset(request).filter(Q(until__gte=timezone.now()) | Q(until=None))

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class MemberGroupMembershipAdmin(admin.ModelAdmin):
    inlines = [MemberGroupMembershipInline]


class BoardInline(admin.TabularInline):
    model = Board
    verbose_name = "Board"
    verbose_name_plural = "Boards"

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


class BoardAdmin(admin.ModelAdmin):
    inlines = [BoardInline]


admin.site.register([Fraternity, Board, YearClub], MemberGroupMembershipAdmin)
# admin.site.register(Fraternity, FraternityAdmin)
