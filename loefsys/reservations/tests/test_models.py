from datetime import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils.timezone import make_aware
from django_dynamic_fixture import G, N

from loefsys.reservations.models import Reservable, Reservation


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
    def test_clean_not_reservable(self):
        reservable = G(Reservable, is_reservable=False)
        new = N(Reservation, reservable=reservable)
        self.assertRaises(ValidationError, new.clean)
