from unittest import mock

from django.core.management import CommandError, call_command
from django.test import TestCase

from loefsys.events.models import Event
from loefsys.members.models import User


class ResetStagingTest(TestCase):
    def test_refuses_without_the_flag(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            with self.assertRaises(CommandError):
                call_command("reset_staging", "--no-wipe")
        self.assertFalse(User.objects.exists())

    def test_creates_invented_data(self):
        env = {"LOEFSYS_ALLOW_RESET": "true", "LOEFSYS_STAGING_PASSWORD": "pw-test-1"}
        with mock.patch.dict("os.environ", env):
            call_command("reset_staging", "--no-wipe", stdout=mock.MagicMock())
        admin = User.objects.get(email="admin@example.org")
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.check_password("pw-test-1"))
        self.assertTrue(
            all(u.email.endswith("@example.org") for u in User.objects.all())
        )
        self.assertTrue(Event.objects.exists())
