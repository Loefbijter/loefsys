"""Authentication backend that also applies permissions of Loefbijter groups."""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth.models import Permission
from django.db.models import Q
from django.utils import timezone

from loefsys.groups.models import LoefbijterGroup


class LoefbijterGroupBackend(ModelBackend):
    """Model backend that grants users the permissions of their Loefbijter groups.

    On top of Django's own groups, a user gets every permission of the Loefbijter
    groups (boards, committees, ...) they currently belong to. A membership counts
    while it has started and hasn't ended, and only for groups that haven't been
    discontinued, so former board members lose the board's permissions.
    """

    def _get_group_permissions(self, user_obj):
        today = timezone.localdate()
        active_group = Q(date_discontinuation__isnull=True) | Q(
            date_discontinuation__gte=today
        )
        active_membership = Q(
            groupmembership__user=user_obj, groupmembership__member_since__lte=today
        ) & (
            Q(groupmembership__member_until__isnull=True)
            | Q(groupmembership__member_until__gte=today)
        )
        groups = LoefbijterGroup.objects.filter(active_group).filter(
            active_membership | Q(user=user_obj)
        )
        return Permission.objects.filter(
            Q(group__user=user_obj) | Q(loefbijtergroup__in=groups)
        ).distinct()
