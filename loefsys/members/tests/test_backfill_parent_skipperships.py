"""Tests for the migration that fills in missing lower skipperships."""

import datetime
from importlib import import_module

from django.apps import apps
from django.test import TestCase

from loefsys.members.models import Skippership, User, UserSkippership

backfill = import_module(
    "loefsys.members.migrations.0011_backfill_parent_skipperships"
).backfill_parent_skipperships


class BackfillParentSkippershipsTestCase(TestCase):
    def test_adds_missing_lower_skipperships(self):
        pico = Skippership.objects.create(name="Pico")
        laser = Skippership.objects.create(name="Laser", parent=pico)
        laser_plus = Skippership.objects.create(name="Laser+", parent=laser)
        kielboot = Skippership.objects.create(name="Kielboot 1")
        user = User.objects.create_user(
            email="sjoerd@example.com",
            password="password",
            first_name="Sjoerd",
            last_name="Golfslag",
        )
        since = datetime.date(2024, 5, 1)
        UserSkippership.objects.create(user=user, skippership=laser_plus, since=since)
        UserSkippership.objects.create(
            user=user, skippership=pico, since=datetime.date(2020, 1, 1)
        )
        UserSkippership.objects.create(user=user, skippership=kielboot, since=since)

        backfill(apps, None)

        held = dict(
            UserSkippership.objects.filter(user=user).values_list(
                "skippership__name", "since"
            )
        )
        self.assertEqual(
            held,
            {
                "Pico": datetime.date(2020, 1, 1),
                "Laser": since,
                "Laser+": since,
                "Kielboot 1": since,
            },
        )
