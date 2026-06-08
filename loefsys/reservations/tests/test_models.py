from datetime import datetime, UTC

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import make_aware
from django_dynamic_fixture import G, N

from loefsys.reservations.models import Reservable, Reservation


class ReservationTimeslotValidationTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.reservable = G(Reservable)
        cls.existing = G(
            Reservation,
            reservable=cls.reservable,
            start=make_aware(datetime(2000, 1, 1, 12, 0, 0)),
            end=make_aware(datetime(2000, 1, 1, 13, 0, 0)),
        )

    def test_overlap_start(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            start=make_aware(datetime(2000, 1, 1, 12, 59, 59)),
            end=make_aware(datetime(2000, 1, 1, 13, 59, 59)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_overlap_end(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            start=make_aware(datetime(2000, 1, 1, 11, 0, 1)),
            end=make_aware(datetime(2000, 1, 1, 12, 0, 1)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_overlap_existing_wraps_new(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            start=make_aware(datetime(2000, 1, 1, 12, 0, 1)),
            end=make_aware(datetime(2000, 1, 1, 12, 59, 59)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_overlap_new_wraps_existing(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            start=make_aware(datetime(2000, 1, 1, 11, 59, 59)),
            end=make_aware(datetime(2000, 1, 1, 13, 0, 1)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_overlap_exact(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            start=make_aware(datetime(2000, 1, 1, 12, 0, 0)),
            end=make_aware(datetime(2000, 1, 1, 13, 0, 0)),
        )
        self.assertRaises(ValidationError, new.clean_timeslot)

    def test_valid_before_existing(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            start=make_aware(datetime(2000, 1, 1, 11, 0, 0)),
            end=make_aware(datetime(2000, 1, 1, 11, 59, 59)),
        )
        new.clean_timeslot()

    def test_valid_after_existing(self):
        new = N(
            Reservation,
            reservable=self.reservable,
            start=make_aware(datetime(2000, 1, 1, 13, 0, 1)),
            end=make_aware(datetime(2000, 1, 1, 13, 59, 59)),
        )
        new.clean_timeslot()


class ReservationTestCase(TestCase):
    def test_clean_not_reservable(self):
        reservable = G(Reservable, is_reservable=False)
        new = N(
            Reservation,
            reservable=reservable,
        )
        self.assertRaises(ValidationError, new.clean)
