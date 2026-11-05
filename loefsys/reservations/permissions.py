"""Who may evaluate (accept or deny) reservation requests.

A reservable can be managed by a group or by a person (see
:class:`~loefsys.reservations.models.reservable.Reservable`). Only its managers
evaluate its requests and see them as a to-do; for a group, that is every active
member. Requests for a reservable without a manager are evaluated by anyone with the
``reservations.change_reservation`` permission. Being a manager alone is enough, no
permission needed; superusers get no exception for managed reservables.
"""

from django.db.models import Q, QuerySet
from django.utils import timezone

from loefsys.groups.models import LoefbijterGroup

from .models import Reservable, Reservation


def _managed_by(user) -> Q:
    """Match the reservables that ``user`` manages, directly or through a group.

    Group memberships count like they do for group permissions (see
    :class:`~loefsys.members.backends.LoefbijterGroupBackend`): started, not ended,
    in a group that hasn't been discontinued.
    """
    today = timezone.localdate()
    groups = LoefbijterGroup.objects.filter(
        Q(date_discontinuation__isnull=True) | Q(date_discontinuation__gte=today),
        Q(groupmembership__member_until__isnull=True)
        | Q(groupmembership__member_until__gte=today),
        groupmembership__user=user,
        groupmembership__member_since__lte=today,
    )
    return Q(managed_by_user=user) | Q(managed_by_group__in=groups)


def evaluable_reservables(user) -> QuerySet[Reservable]:
    """Return the reservables whose requests ``user`` may evaluate."""
    if not (user.is_authenticated and user.is_active):
        return Reservable.objects.none()
    condition = _managed_by(user)
    if user.has_perm("reservations.change_reservation"):
        condition |= Q(managed_by_user__isnull=True, managed_by_group__isnull=True)
    return Reservable.objects.filter(condition)


def evaluable_reservations(user) -> QuerySet[Reservation]:
    """Return the reservations that ``user`` may evaluate."""
    return Reservation.objects.filter(reservable__in=evaluable_reservables(user))


def can_evaluate(user, reservation: Reservation) -> bool:
    """Return whether ``user`` may accept or deny ``reservation``."""
    return evaluable_reservables(user).filter(pk=reservation.reservable_id).exists()


def manages_reservables(user) -> bool:
    """Return whether ``user`` manages at least one reservable."""
    if not (user.is_authenticated and user.is_active):
        return False
    return Reservable.objects.filter(_managed_by(user)).exists()
