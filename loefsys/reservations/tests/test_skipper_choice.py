"""Tests for choosing the skipper of a boat reservation."""

import datetime

from django.core.exceptions import ValidationError
from django.test import TestCase

from loefsys.members.models import Skippership, User, UserSkippership
from loefsys.members.models.choices import DisplayNamePreferences
from loefsys.reservations.forms import CreateReservationForm
from loefsys.reservations.models import ReservableBoat, ReservableType, Reservation
from loefsys.reservations.models.choices import Locations, ReservableCategories


class SkipperChoiceTestCase(TestCase):
    laser: Skippership
    laser_plus: Skippership
    kielboot: Skippership
    laser_skipper: User
    keel_skipper: User
    non_skipper: User
    boat: ReservableBoat

    @classmethod
    def setUpTestData(cls):
        cls.laser = Skippership.objects.create(name="Laser")
        cls.laser_plus = Skippership.objects.create(name="Laser+", parent=cls.laser)
        cls.kielboot = Skippership.objects.create(name="Kielboot 1")

        cls.laser_skipper = User.objects.create_user(
            email="wessel@example.com",
            password="password",
            first_name="Wessel",
            last_name="Zeilstra",
            initials="W.",
            display_name_preference=DisplayNamePreferences.INITIALS_LASTNAME,
        )
        UserSkippership.objects.create(
            user=cls.laser_skipper, skippership=cls.laser_plus
        )
        cls.keel_skipper = User.objects.create_user(
            email="fenna@example.com",
            password="password",
            first_name="Fenna",
            last_name="Kielstra",
        )
        UserSkippership.objects.create(user=cls.keel_skipper, skippership=cls.kielboot)
        cls.non_skipper = User.objects.create_user(
            email="joost@example.com",
            password="password",
            first_name="Joost",
            last_name="Landrot",
        )

        boat_type = ReservableType.objects.create(
            name="Laser", category=ReservableCategories.BOAT, description="A boat"
        )
        cls.boat = ReservableBoat.objects.create(
            name="Rimpel",
            description="A boat",
            type=boat_type,
            location=Locations.BASTION,
            is_reservable=True,
            capacity=1,
            has_engine=False,
            provider=ReservableBoat.Provider.LOEFBIJTER,
            requires_skippership=cls.laser,
        )

    def options_by_user(self):
        return {
            option["user"]: option for option in CreateReservationForm().skipper_options
        }

    def test_only_skippers_are_offered(self):
        options = self.options_by_user()
        self.assertIn(self.laser_skipper, options)
        self.assertIn(self.keel_skipper, options)
        self.assertNotIn(self.non_skipper, options)

    def test_higher_skippership_also_qualifies_for_lower(self):
        skipperships = self.options_by_user()[self.laser_skipper]["skipperships"]
        self.assertEqual(
            set(skipperships.split(",")), {str(self.laser.pk), str(self.laser_plus.pk)}
        )

    def test_search_text_includes_full_name(self):
        # The display name is "W. Zeilstra", but searching "wessel zeil" must match.
        search = self.options_by_user()[self.laser_skipper]["search"]
        self.assertIn("wessel", search)
        self.assertIn("zeilstra", search)

    def reservation(self, skipper):
        return Reservation(
            reservable=self.boat,
            user=self.non_skipper,
            authorized_userskippership=skipper,
            start=datetime.datetime(2030, 6, 1, 11, 0, tzinfo=datetime.UTC),
            end=datetime.datetime(2030, 6, 1, 12, 0, tzinfo=datetime.UTC),
            reason="Training",
        )

    def test_reservation_accepts_skipper_with_higher_skippership(self):
        self.reservation(self.laser_skipper).clean()

    def test_reservation_rejects_unqualified_skipper(self):
        with self.assertRaises(ValidationError):
            self.reservation(self.keel_skipper).clean()
