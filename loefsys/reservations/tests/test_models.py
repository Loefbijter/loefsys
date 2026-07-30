from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import make_aware
from django_dynamic_fixture import G, N

from loefsys.members.models.user import User
from loefsys.reservations.models import ReservableType, Reservation
from loefsys.reservations.models.choices import (
    Locations,
    ReservableCategories,
    ReservationStatus,
)
from loefsys.reservations.models.reservable import ReservableItem


class ReservationTimeslotValidationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reservable = G(Reservable)
        cls.approved_reservation = G(
            Reservation,
            reservable=cls.reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 12, 0, 0)),
            end=make_aware(datetime(2000, 1, 1, 13, 0, 0)),
        )

    def test_overlap_start(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 12, 59, 59)),
            end=make_aware(datetime(2000, 1, 1, 13, 59, 59)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_overlap_end(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 11, 0, 1)),
            end=make_aware(datetime(2000, 1, 1, 12, 0, 1)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_overlap_existing_wraps_new(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 12, 0, 1)),
            end=make_aware(datetime(2000, 1, 1, 12, 59, 59)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_overlap_new_wraps_existing(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 11, 59, 59)),
            end=make_aware(datetime(2000, 1, 1, 13, 0, 1)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_overlap_exact(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 12, 0, 0)),
            end=make_aware(datetime(2000, 1, 1, 13, 0, 0)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_valid_before_existing(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 11, 0, 0)),
            end=make_aware(datetime(2000, 1, 1, 11, 59, 59)),
        )
        new.clean_timeslot()

    def test_valid_after_existing(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 13, 0, 1)),
            end=make_aware(datetime(2000, 1, 1, 13, 59, 59)),
        )
        new.clean_timeslot()

    def test_pending_does_not_block_timeslot(self):
        pending_reservable = G(Reservable)

        G(
            Reservation,
            reservable=pending_reservable,
            request_status=Reservation.RequestStatus.PENDING,
            start=make_aware(datetime(2000, 1, 1, 12, 0)),
            end=make_aware(datetime(2000, 1, 1, 13, 0)),
        )

        new = N(
            Reservation,
            reservable=pending_reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 12, 30)),
            end=make_aware(datetime(2000, 1, 1, 13, 30)),
        )

        new.clean_timeslot()

    def test_denied_does_not_block_timeslot(self):
        denied_reservable = G(Reservable)

        G(
            Reservation,
            reservable=denied_reservable,
            request_status=Reservation.RequestStatus.DENIED,
            start=make_aware(datetime(2000, 1, 1, 12, 0)),
            end=make_aware(datetime(2000, 1, 1, 13, 0)),
        )

        new = N(
            Reservation,
            reservable=denied_reservable,
            request_status=Reservation.RequestStatus.APPROVED,
            start=make_aware(datetime(2000, 1, 1, 12, 30)),
            end=make_aware(datetime(2000, 1, 1, 13, 30)),
        )

        new.clean_timeslot()


class ReservationTestCase(TestCase):
    """Tests for Reservation model creation and validation."""

    def setUp(self):
        self.reservable_type = ReservableType(
            name="Room", category=ReservableCategories.ROOM, description="GiPHouse room"
        )
        self.reservable_type.save()

        self.reservable_item = ReservableItem(
            name="Reservable room",
            description="A room",
            reservable_type=self.reservable_type,
            location=Locations.KRAAIJ,
            is_reservable=True,
        )
        self.reservable_item.save()

        self.unreservable_item = ReservableItem(
            name="Unreservable room",
            description="A room",
            reservable_type=self.reservable_type,
            location=Locations.KRAAIJ,
            is_reservable=False,
        )
        self.unreservable_item.save()

        self.reservee_user = User.objects.create_user(
            email="dummy@dummy.nl", password="1234"
        )
        self.reservee_user.save()

    def test_create(self):
        """Tests that Reservation instance can be created."""
        reservation = Reservation(
            reserved_item=self.reservable_item,
            reservee_user=self.reservee_user,
            start=datetime.datetime(2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC),
            end=datetime.datetime(2025, 1, 1, hour=13, minute=0, tzinfo=datetime.UTC),
        )
        reservation.save()
        self.assertIsNotNone(reservation)
        self.assertIsNotNone(reservation.pk)

    def test_same_start_end(self):
        """Tests that Reservation instance cannot be created with the same start and end time."""  # noqa: E501
        with self.assertRaises(IntegrityError):
            reservation = Reservation(
                reserved_item=self.reservable_item,
                reservee_user=self.reservee_user,
                start=datetime.datetime(
                    2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC
                ),
                end=datetime.datetime(
                    2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC
                ),
            )
            reservation.save()

    def test_start_after_end(self):
        """Tests that Reservation instance cannot be created with the start after the end time."""  # noqa: E501
        with self.assertRaises(IntegrityError):
            reservation = Reservation(
                reserved_item=self.reservable_item,
                reservee_user=self.reservee_user,
                start=datetime.datetime(
                    2025, 1, 1, hour=13, minute=0, tzinfo=datetime.UTC
                ),
                end=datetime.datetime(
                    2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC
                ),
            )
            reservation.save()

    def test_reserved_twice(self):
        """Tests that two Reservation instances can be created for the same item on different timeslots."""  # noqa: E501
        reservation1 = Reservation(
            reserved_item=self.reservable_item,
            reservee_user=self.reservee_user,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC),
        )
        reservation1.save()

        reservation2 = Reservation(
            reserved_item=self.reservable_item,
            reservee_user=self.reservee_user,
            start=datetime.datetime(2025, 1, 1, hour=13, minute=0, tzinfo=datetime.UTC),
            end=datetime.datetime(2025, 1, 1, hour=14, minute=0, tzinfo=datetime.UTC),
        )
        reservation2.save()

        self.assertIsNotNone(reservation1)
        self.assertIsNotNone(reservation2)

    def test_reserved_twice_overlap(self):
        """Tests that two Reservation instances can be created for the same item on overlapping timeslots."""  # noqa: E501
        with self.assertRaises(ValidationError):
            reservation1 = Reservation(
                reserved_item=self.reservable_item,
                reservee_user=self.reservee_user,
                start=datetime.datetime(
                    2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC
                ),
                end=datetime.datetime(
                    2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC
                ),
            )
            reservation1.save()
            reservation1.clean()

            reservation2 = Reservation(
                reserved_item=self.reservable_item,
                reservee_user=self.reservee_user,
                start=datetime.datetime(
                    2025, 1, 1, hour=11, minute=30, tzinfo=datetime.UTC
                ),
                end=datetime.datetime(
                    2025, 1, 1, hour=13, minute=0, tzinfo=datetime.UTC
                ),
            )
            reservation2.save()
            reservation2.clean()

    def test_duplicate(self):
        """Tests that two duplicate Reservation instances cannot be created."""
        with self.assertRaises(ValidationError):
            reservation1 = Reservation(
                reserved_item=self.reservable_item,
                reservee_user=self.reservee_user,
                start=datetime.datetime(
                    2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC
                ),
                end=datetime.datetime(
                    2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC
                ),
            )
            reservation1.save()

            reservation2 = Reservation(
                reserved_item=self.reservable_item,
                reservee_user=self.reservee_user,
                start=datetime.datetime(
                    2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC
                ),
                end=datetime.datetime(
                    2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC
                ),
            )
            reservation2.clean()
            reservation2.save()

    def test_reserved_two_overlap(self):
        """Tests that two Reservation instances can be created for two items on overlapping timeslots."""  # noqa: E501
        reservable_item2 = ReservableItem(
            name="Large room",
            description="A room",
            reservable_type=self.reservable_type,
            location=Locations.KRAAIJ,
            is_reservable=True,
        )
        reservable_item2.save()

        reservation1 = Reservation(
            reserved_item=self.reservable_item,
            reservee_user=self.reservee_user,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC),
        )
        reservation1.save()

        reservation2 = Reservation(
            reserved_item=reservable_item2,
            reservee_user=self.reservee_user,
            start=datetime.datetime(
                2025, 1, 1, hour=11, minute=30, tzinfo=datetime.UTC
            ),
            end=datetime.datetime(2025, 1, 1, hour=13, minute=0, tzinfo=datetime.UTC),
        )
        reservation2.clean()
        reservation2.save()

        self.assertIsNotNone(reservation1)
        self.assertIsNotNone(reservation2)

    def test_is_reservable(self):
        """Tests that an item that has the is_reservable field as true can be reserved."""  # noqa: E501
        reservation = Reservation(
            reserved_item=self.reservable_item,
            reservee_user=self.reservee_user,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC),
        )
        reservation.save()

        self.assertIsNotNone(reservation)

    def test_is_not_reservable(self):
        """Tests that an item that has the is_reservable field as true can be reserved."""  # noqa: E501
        with self.assertRaises(ValidationError):
            reservation = Reservation(
                reserved_item=self.unreservable_item,
                reservee_user=self.reservee_user,
                start=datetime.datetime(
                    2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC
                ),
                end=datetime.datetime(
                    2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC
                ),
            )
            reservation.save()
            reservation.clean()

    def test_denied_requires_reason(self):
        """Tests that denying a reservation requires a denial reason."""
        reservation = Reservation(
            reserved_item=self.reservable_item,
            reservee_user=self.reservee_user,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC),
            status=ReservationStatus.DENIED,
        )

        with self.assertRaises(ValidationError):
            reservation.full_clean()

    def test_denied_with_reason_is_valid(self):
        """Tests that denying a reservation with a reason is valid."""
        reservation = Reservation(
            reserved_item=self.reservable_item,
            reservee_user=self.reservee_user,
            start=datetime.datetime(2025, 1, 1, hour=11, minute=0, tzinfo=datetime.UTC),
            end=datetime.datetime(2025, 1, 1, hour=12, minute=0, tzinfo=datetime.UTC),
            status=ReservationStatus.DENIED,
            denial_reason="Boat already reserved for a club activity.",
        )

        reservation.full_clean()
        reservation.save()
        self.assertEqual(reservation.status, ReservationStatus.DENIED)
