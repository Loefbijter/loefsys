"""Sync user is_staff flag based on active board memberships."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.timezone import now

from loefsys.groups.models.board import Board
from loefsys.groups.models.membership import GroupMembership


class Command(BaseCommand):
    """Django management command to sync user staff status with board memberships."""

    help = "Sync user.is_staff according to active board memberships"

    def handle(self, *_args, **_options):
        """Sync staff flags for all users based on their active board memberships."""
        user_model = get_user_model()
        today = now().date()

        active_boards = Board.objects.filter(
            Q(date_discontinuation__isnull=True) | Q(date_discontinuation__gte=today)
        )
        memberships = GroupMembership.objects.filter(
            group__in=active_boards
        ).select_related("user")

        users_to_mark = set(m.user for m in memberships)

        updated = 0
        # First, set is_staff=True for users in users_to_mark
        for user in users_to_mark:
            if not user.is_staff:
                user.is_staff = True
                user.save(update_fields=["is_staff"])
                updated += 1

        # Unset is_staff for users who are not superuser and have no active board
        # membership
        all_users = user_model.objects.exclude(is_superuser=True).all()
        unset_count = 0
        for u in all_users:
            has_active = GroupMembership.objects.filter(
                user=u, group__in=active_boards
            ).exists()
            if not has_active and u.is_staff:
                u.is_staff = False
                u.save(update_fields=["is_staff"])
                unset_count += 1

        message = (
            f"Marked {updated} users as staff; removed staff from {unset_count} users."
        )
        self.stdout.write(self.style.SUCCESS(message))
