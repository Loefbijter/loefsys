"""Wipe the database and fill it with invented data, for the staging server.

Every name, email address and phone number created here is made up. Never load real
members' details into staging.

The command refuses to run unless ``LOEFSYS_ALLOW_RESET=true`` is set, so it can't
wipe production by accident. The password for every created user comes from
``LOEFSYS_STAGING_PASSWORD``; without it a random one is generated and printed.
"""

import os
import random
import secrets
from datetime import date, timedelta
from decimal import Decimal

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.utils import timezone

from loefsys.events.models import Event, EventOrganizer, EventRegistration
from loefsys.events.models.choices import EventCategories, RegistrationStatus
from loefsys.groups.models import Board, Committee
from loefsys.groups.models.membership import GroupMembership
from loefsys.members.models import Membership, Skippership, User, UserSkippership
from loefsys.members.models.choices import MembershipTypes
from loefsys.reservations.models.boat import ReservableBoat
from loefsys.reservations.models.choices import Locations, ReservableCategories
from loefsys.reservations.models.reservable import Reservable, ReservableType
from loefsys.reservations.models.reservation import Reservation

FIRST_NAMES = (
    "Anouk Bram Daan Eva Femke Gijs Hanna Jesse Julia Kees Lotte Maarten Noor Pim "
    "Roos Sanne Thijs Tess Vera Wouter Yara Zeger Iris Joost Mila Ruben Sterre Teun"
).split()
LAST_NAMES = (
    "de Wind|van Stuurboord|Bakboord|Zeilmaker|de Kiel|van der Mast|Golfslag|"
    "Ankerman|de Boei|Fokkema|van Loef|Schoot|Roerdink|de Vries-Testpersoon"
).split("|")

COMMITTEES = (
    "Activiteitencommissie",
    "Botencommissie",
    "Wedstrijdcommissie",
    "Introductiecommissie",
)

EVENTS = (
    ("Openingsborrel", EventCategories.ASSOCIATION, -40),
    ("Instructiedag kielboot", EventCategories.TRAINING, -12),
    ("Kroegentocht op het water", EventCategories.LEISURE, -3),
    ("Zeilweekend Friesland", EventCategories.SAILING, 5),
    ("Clubkampioenschap", EventCategories.COMPETITION, 9),
    ("Alumnidiner", EventCategories.ALUMNI, 16),
    ("Algemene ledenvergadering", EventCategories.ASSOCIATION, 23),
    ("Pubquiz", EventCategories.LEISURE, 30),
)

BOATS = ("Zwerver", "Windekind", "Stormvogel", "Meeuw")


class Command(BaseCommand):
    """Wipe the database, migrate it and fill it with invented data."""

    help = "Wipe the database and fill it with invented data (staging only)."

    def add_arguments(self, parser):  # noqa: D102
        parser.add_argument(
            "--no-wipe",
            action="store_true",
            help="Only add the invented data; keep what is already in the database.",
        )

    def handle(self, *_args, **options):  # noqa: D102
        if os.environ.get("LOEFSYS_ALLOW_RESET", "").lower() != "true":
            raise CommandError(
                "Refusing to reset: set LOEFSYS_ALLOW_RESET=true. "
                "Only the staging server should have it."
            )
        password = os.environ.get("LOEFSYS_STAGING_PASSWORD") or secrets.token_urlsafe(
            12
        )

        if not options["no_wipe"]:
            self.stdout.write("Dropping every table...")
            drop_all_tables()
        call_command("migrate", interactive=False, verbosity=0)

        self.stdout.write("Creating invented data...")
        with transaction.atomic():
            seed(password)

        self.stdout.write(self.style.SUCCESS("Staging data is reset."))
        self.stdout.write("Log in as admin@example.org (superuser) or lid1@example.org")
        if "LOEFSYS_STAGING_PASSWORD" not in os.environ:
            self.stdout.write(f"Generated password for every user: {password}")


def drop_all_tables() -> None:
    """Drop every table, so ``migrate`` rebuilds the schema from scratch."""
    tables = connection.introspection.table_names()
    with connection.cursor() as cursor:
        if connection.vendor == "postgresql":
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}" CASCADE')
        else:
            cursor.execute("PRAGMA foreign_keys = OFF")
            for table in tables:
                cursor.execute(f'DROP TABLE IF EXISTS "{table}"')
            cursor.execute("PRAGMA foreign_keys = ON")


def seed(password: str) -> None:
    """Create invented members, groups, skipperships, boats, events and reservations."""
    rng = random.Random(2026)
    today = timezone.localdate()

    User.objects.create_superuser(
        email="admin@example.org",
        password=password,
        first_name="Admin",
        last_name="Staging",
    )
    members = []
    for i in range(1, 29):
        first = FIRST_NAMES[(i - 1) % len(FIRST_NAMES)]
        user = User.objects.create_user(
            email=f"lid{i}@example.org",
            password=password,
            first_name=first,
            last_name=rng.choice(LAST_NAMES),
            nickname=first[:3] if i % 4 == 0 else "",
            lichting=f"{50 + i % 8}e lichting",
            birthday=date(1998 + i % 8, 1 + i % 12, 1 + i % 28),
            phone_number=f"+3161234{i:04d}",
        )
        Membership.objects.create(
            member=user,
            membership_type=MembershipTypes.PASSIVE
            if i % 7 == 0
            else MembershipTypes.ACTIVE,
            start=date(2018 + i % 8, 9, 1),
        )
        members.append(user)

    board = Board.objects.create(
        name=f"Bestuur {today.year}",
        description="Het verzonnen bestuur van staging.",
        date_foundation=date(today.year, 1, 1),
        display_members=True,
        year=today.year,
    )
    for i, (user, role) in enumerate(
        zip(members[:4], ("Voorzitter", "Secretaris", "Penningmeester", "Commissaris"))
    ):
        add_member(board, user, role=role, chair=i == 0)

    for n, name in enumerate(COMMITTEES):
        committee = Committee.objects.create(
            name=name,
            description=f"De verzonnen {name.lower()}.",
            date_foundation=date(2010 + n, 1, 1),
            display_members=True,
            mandatory=False,
        )
        for j, user in enumerate(rng.sample(members[4:], 4)):
            add_member(committee, user, chair=j == 0)

    kb1 = Skippership.objects.create(name="Kielboot 1")
    kb2 = Skippership.objects.create(name="Kielboot 2", parent=kb1)
    Skippership.objects.create(name="Kielboot 3", parent=kb2)
    pico = Skippership.objects.create(name="Pico")
    for user in members[::3]:
        UserSkippership.objects.create(
            user=user, skippership=kb1, since=date(2024, 5, 1)
        )
    for user in members[1::5]:
        UserSkippership.objects.create(
            user=user, skippership=pico, since=date(2025, 4, 1)
        )

    boat_type = ReservableType.objects.create(
        name="Kielboot",
        category=ReservableCategories.BOAT,
        description="Verzonnen boottype.",
    )
    room_type = ReservableType.objects.create(
        name="Vergaderruimte",
        category=ReservableCategories.ROOM,
        description="Verzonnen ruimtetype.",
    )
    boats = [
        ReservableBoat.objects.create(
            name=name,
            description="Een verzonnen boot.",
            type=boat_type,
            location=Locations.KRAAIJ,
            is_reservable=True,
            capacity=4,
        )
        for name in BOATS
    ]
    room = Reservable.objects.create(
        name="Bestuurskamer",
        description="Een verzonnen ruimte.",
        type=room_type,
        location=Locations.BOARDROOM,
        is_reservable=True,
    )
    now = timezone.now().replace(minute=0, second=0, microsecond=0)
    for k, reservable in enumerate([*boats, room] * 2):
        start = now + timedelta(days=k - 3, hours=10 - now.hour)
        Reservation.objects.create(
            user=members[(k * 3) % len(members)],
            reservable=reservable,
            start=start,
            end=start + timedelta(hours=3),
            reason="Verzonnen reservering.",
        )

    for title, category, days in EVENTS:
        event = make_event(
            title, category, now + timedelta(days=days, hours=20 - now.hour)
        )
        organizer, _ = EventOrganizer.objects.get_or_create(event=event)
        organizer.user.add(rng.choice(members[:8]))
        for user in rng.sample(members, rng.randint(5, 15)):
            EventRegistration.objects.create(
                event=event,
                contact=user,
                price_at_registration=event.price,
                fine_at_registration=event.fine,
                costs_paid=Decimal("0.00"),
                status=RegistrationStatus.ACTIVE,
            )


def add_member(group, user: User, role: str = "", chair: bool = False) -> None:
    """Make ``user`` a current member of ``group``."""
    GroupMembership.objects.create(
        user=user,
        group=group,
        role=role,
        chair=chair,
        member_since=group.date_foundation,
    )
    user.loefbijter_groups.add(group)


def make_event(title: str, category: int, start) -> Event:
    """Create a published event that starts at ``start`` and lasts three hours."""
    registration_start = start - timedelta(days=21)
    return Event.objects.create(
        title=title,
        description="Een verzonnen activiteit op staging.",
        start=start,
        end=start + timedelta(hours=3),
        registration_start=registration_start,
        registration_deadline=start - timedelta(hours=1),
        cancelation_deadline=start - timedelta(days=1),
        category=category,
        capacity=30,
        price=Decimal("5.00"),
        fine=Decimal("2.50"),
        location="Steiger Testhaven",
        is_open_event=False,
        published=True,
        send_cancel_email=False,
    )
