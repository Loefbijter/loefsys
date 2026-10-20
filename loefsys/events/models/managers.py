"""Module containing all model managers for the events app."""

from typing import TYPE_CHECKING

from django.db import models
from django.db.models import Q
from django.db.models.functions import Now

from loefsys.groups.models.membership import GroupMembership
from loefsys.members.models import User

from .choices import RegistrationStatus

if TYPE_CHECKING:
    from .event import Event
    from .registration import EventRegistration


class EventManager[TEvent: "Event"](models.Manager[TEvent]):
    """Model manager for events."""

    def active(self) -> models.QuerySet["Event"]:
        """Filter for events that are going to happen or are currently ongoing.

        Returns
        -------
        ~django.db.models.query.QuerySet of ~loefsys.events.models.event.Event
            A query of all active events.
        """
        return self.filter(event_end__lte=Now())

    def visible_to(self, user) -> models.QuerySet["Event"]:
        """Filter for events that the given user is allowed to see.

        Everyone sees published events. Board members, users who may change events
        and the organizers of an event also see it while it is unpublished.

        Returns
        -------
        ~django.db.models.query.QuerySet of ~loefsys.events.models.event.Event
            A query of all events visible to the user.
        """
        if can_see_all_unpublished_events(user):
            return self.all()
        published = Q(published=True)
        if not user.is_authenticated:
            return self.filter(published)
        groups = _active_memberships(user).values("group")
        return self.filter(
            published
            | Q(eventorganizer__user=user)
            | Q(eventorganizer__groups__in=groups)
        ).distinct()


def can_see_all_unpublished_events(user) -> bool:
    """Return whether the user may see every unpublished event.

    That is the case for current board members and anyone who may change events.
    """
    if not user.is_authenticated:
        return False
    if user.has_perm("events.change_event"):
        return True
    return _active_memberships(user).filter(group__board__isnull=False).exists()


def _active_memberships(user):
    """Return the group memberships of the user that have not ended."""
    return GroupMembership.objects.filter(
        Q(member_until__isnull=True) | Q(member_until__gte=Now()), user=user
    )


# TODO fix typing
class EventRegistrationManager(models.Manager["EventRegistration"]):
    """Custom manager for :class:`~loefsys.events.models.EventRegistration` models."""

    def order_by_creation(self) -> models.QuerySet["EventRegistration"]:
        """Allow a query to be sorted by creation.

        Returns
        -------
        ~django.db.models.query.QuerySet of ~loefsys.events.models.EventRegistration
            A query sorted by creation timestamp.
        """
        return self.order_by("created")

    def active(self) -> models.QuerySet["EventRegistration"]:
        """Filter and only return active registrations.

        Returns
        -------
        ~django.db.models.query.QuerySet of ~loefsys.events.models.EventRegistration
            A query containing active registrations only.
        """
        return self.filter(status=RegistrationStatus.ACTIVE)

    def queued(self) -> models.QuerySet["EventRegistration"]:
        """Filter and only return queued registrations.

        Returns
        -------
        ~django.db.models.query.QuerySet of ~loefsys.events.models.EventRegistration
            A query containing queued registrations only.
        """
        return self.filter(status=RegistrationStatus.QUEUED)

    def cancelled(self) -> models.QuerySet["EventRegistration"]:
        """Filter and only return cancelled registrations.

        Returns
        -------
        ~django.db.models.query.QuerySet of ~loefsys.events.models.EventRegistration
            A query containing cancelled registrations only.
        """
        return self.filter(
            Q(status=RegistrationStatus.CANCELLED_FINE)
            | Q(status=RegistrationStatus.CANCELLED_NOFINE)
        )

    def for_user(self, user: User) -> models.QuerySet["EventRegistration"]:
        """Filter registrations for a specific user.

        Returns
        -------
        ~django.db.models.query.QuerySet of ~loefsys.events.models.EventRegistration
            A query containing registrations for the specified user.
        """
        return self.filter(contact=user)
