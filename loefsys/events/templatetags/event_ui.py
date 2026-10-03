"""Template helpers for the event widgets (``<c-event-row>``, ``<c-event-hero>``)."""

from django import template

from loefsys.events.models import Event, EventRegistration
from loefsys.events.models.choices import EventCategories, RegistrationStatus

register = template.Library()


@register.filter
def category_key(category: int) -> str:
    """Return the CSS key for an event category, as used by ``.cat-<key>``."""
    try:
        return EventCategories(category).name.lower()
    except ValueError:
        return "other"


@register.filter
def spots_left(event: Event) -> int | None:
    """Return the number of free places, or ``None`` when there is no limit."""
    if not event.capacity:
        return None
    return max(0, event.capacity - event.eventregistration_set.active().count())


@register.simple_tag
def registration_for(event: Event, user) -> EventRegistration | None:
    """Return the user's active or queued registration for an event, if any."""
    if not getattr(user, "is_authenticated", False):
        return None
    return EventRegistration.objects.filter(
        event=event,
        contact=user,
        status__in=(RegistrationStatus.ACTIVE, RegistrationStatus.QUEUED),
    ).first()
