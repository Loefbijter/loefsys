"""Invented test data for the end-to-end tests.

Every name, email address and phone number here is made up. Never use real members'
details in tests.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, Permission
from django.utils import timezone

from loefsys.events.models import Event, EventOrganizer, EventRegistration
from loefsys.events.models.choices import EventCategories, RegistrationStatus
from loefsys.members.models import Skippership, User, UserSkippership
from loefsys.reservations.models.boat import ReservableBoat
from loefsys.reservations.models.choices import Locations, ReservableCategories
from loefsys.reservations.models.reservable import Reservable, ReservableType
from loefsys.reservations.models.reservation import Reservation

PASSWORD = "Zeilwind-e2e-2026!"
"""Password shared by every user created here."""


def make_user(
    email: str = "testa.zeilmaker@example.org",
    first_name: str = "Testa",
    last_name: str = "Zeilmaker",
    **extra,
) -> User:
    """Create an active member who can log in with :data:`PASSWORD`."""
    return User.objects.create_user(
        email=email,
        password=PASSWORD,
        first_name=first_name,
        last_name=last_name,
        **extra,
    )


def make_event(
    title: str = "Kroegentocht op het water",
    *,
    days_ahead: int = 7,
    start: datetime | None = None,
    capacity: int | None = None,
    published: bool = True,
    registration_open: bool = True,
    category: int = EventCategories.LEISURE,
    location: str = "Steiger Testhaven",
    description: str = "Een verzonnen activiteit voor de end-to-end tests.",
    **extra,
) -> Event:
    """Create an event that starts at ``start``, or ``days_ahead`` days from now."""
    now = timezone.now()
    start = start or now + timedelta(days=days_ahead)
    if registration_open:
        # Open well before both now and the start, so the deadlines below stay after
        # it even for an event earlier today (such as the calendar's noon events).
        registration_start = min(now, start) - timedelta(days=2)
    else:
        registration_start = start - timedelta(days=3)
    registration_deadline = start - timedelta(hours=1)
    return Event.objects.create(
        title=title,
        description=description,
        start=start,
        end=start + timedelta(hours=3),
        registration_start=registration_start,
        registration_deadline=registration_deadline,
        cancelation_deadline=max(start - timedelta(days=1), registration_start),
        category=category,
        capacity=capacity,
        price=Decimal("0.00"),
        fine=Decimal("0.00"),
        location=location,
        is_open_event=False,
        published=published,
        send_cancel_email=False,
        **extra,
    )


def register(event: Event, user: User) -> EventRegistration:
    """Register ``user`` for ``event``."""
    return EventRegistration.objects.create(
        event=event,
        contact=user,
        price_at_registration=event.price,
        fine_at_registration=event.fine,
        costs_paid=Decimal("0.00"),
        status=RegistrationStatus.ACTIVE,
    )


def make_organizer(event: Event, user: User) -> EventOrganizer:
    """Make ``user`` an organizer of ``event``."""
    organizer, _ = EventOrganizer.objects.get_or_create(event=event)
    organizer.user.add(user)
    return organizer


def make_skipperships() -> dict[str, Skippership]:
    """Create a small skippership tree: Kielboot 1 -> 2 -> 3, plus Pico."""
    kb1 = Skippership.objects.create(name="Kielboot 1")
    kb2 = Skippership.objects.create(name="Kielboot 2", parent=kb1)
    kb3 = Skippership.objects.create(name="Kielboot 3", parent=kb2)
    pico = Skippership.objects.create(name="Pico")
    return {"kb1": kb1, "kb2": kb2, "kb3": kb3, "pico": pico}


def grant_skippership(user: User, *skipperships: Skippership) -> None:
    """Give ``user`` each of ``skipperships``."""
    for skippership in skipperships:
        UserSkippership.objects.create(
            user=user, skippership=skippership, since=date(2024, 5, 1)
        )


def make_boat(
    name: str = "Zwerver", location: int = Locations.KRAAIJ, **extra
) -> ReservableBoat:
    """Create a reservable boat."""
    boat_type, _ = ReservableType.objects.get_or_create(
        name="Kielboot",
        defaults={
            "category": ReservableCategories.BOAT,
            "description": "Verzonnen boottype.",
        },
    )
    return ReservableBoat.objects.create(
        name=name,
        description="Een verzonnen boot voor de tests.",
        type=boat_type,
        location=location,
        is_reservable=True,
        capacity=4,
        **extra,
    )


def make_room(name: str = "Testkamer", location: int = Locations.BOARDROOM):
    """Create a reservable room."""
    room_type, _ = ReservableType.objects.get_or_create(
        name="Vergaderruimte",
        defaults={
            "category": ReservableCategories.ROOM,
            "description": "Verzonnen ruimtetype.",
        },
    )
    return Reservable.objects.create(
        name=name,
        description="Een verzonnen ruimte voor de tests.",
        type=room_type,
        location=location,
        is_reservable=True,
    )


def make_reservation(user: User, reservable: Reservable, days_ahead: int = 3, **extra):
    """Create a reservation of two hours, ``days_ahead`` days from now."""
    start = (timezone.now() + timedelta(days=days_ahead)).replace(
        minute=0, second=0, microsecond=0
    )
    return Reservation.objects.create(
        user=user,
        reservable=reservable,
        start=start,
        end=start + timedelta(hours=2),
        **extra,
    )


def grant_permissions(user: User, *perms: str) -> None:
    """Give ``user`` the permissions named ``app_label.codename``."""
    for perm in perms:
        app_label, codename = perm.split(".")
        user.user_permissions.add(
            Permission.objects.get(content_type__app_label=app_label, codename=codename)
        )


def add_to_group(user: User, name: str) -> Group:
    """Add ``user`` to the Django group called ``name``."""
    group = Group.objects.get(name=name)
    user.groups.add(group)
    return group
