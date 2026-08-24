"""Signal handlers to automatically sync user staff status with board memberships."""

from django.contrib.auth import get_user_model
from django.db.models import Q
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from django.utils.timezone import now

from .models.board import Board
from .models.membership import GroupMembership

User = get_user_model()


def _user_has_active_board_membership(user) -> bool:
    """Return True if the given user has any active membership in a Board.

    Active boards are those where date_discontinuation is null or >= today.
    """
    today = now().date()
    return GroupMembership.objects.filter(
        user=user,
        group__in=Board.objects.filter(
            Q(date_discontinuation__isnull=True) | Q(date_discontinuation__gte=today)
        ),
    ).exists()


def _update_user_staff(user):
    """Ensure user.is_staff reflects whether they are currently on an active board.

    Users who are superusers retain is_staff=True.
    """
    if user is None:
        return
    try:
        should_be_staff = user.is_superuser or _user_has_active_board_membership(user)
        if user.is_staff != should_be_staff:
            user.is_staff = should_be_staff
            # Avoid updating modified timestamps elsewhere by saving only the field
            user.save(update_fields=["is_staff"])
    except Exception:
        # Be defensive in signal handlers; don't let exceptions bubble up.
        return


@receiver(post_save, sender=GroupMembership)
def _on_membership_saved(_sender, instance, **_kwargs):
    """When a membership is created or updated, ensure user's staff status matches."""
    _update_user_staff(instance.user)


@receiver(post_delete, sender=GroupMembership)
def _on_membership_deleted(_sender, instance, **_kwargs):
    """When a membership is removed, ensure user's staff status updates."""
    _update_user_staff(instance.user)


@receiver(post_save, sender=Board)
def _on_board_saved(_sender, instance, **_kwargs):
    """When a board is saved, update staff status of its members.

    For example, when date_discontinuation changes, this keeps staff flags in sync
    when a board term expires or is reinstated.
    """
    # Iterate over related memberships and update their users
    memberships = GroupMembership.objects.filter(group=instance)
    for m in memberships.select_related("user"):
        _update_user_staff(m.user)
