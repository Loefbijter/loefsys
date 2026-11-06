from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G

from loefsys.members.models import Membership, Skippership, UserSkippership
from loefsys.members.models.choices import MembershipTypes


class SchippersViewTestCase(TestCase):
    """Tests for the schippers page grouping logic."""

    def test_schippers_page_displays_non_kb_skipperships(self):
        """The page includes skipperships that are not part of a KB hierarchy."""
        user = G(get_user_model())
        skippership = G(Skippership, name="Kielboot")
        G(UserSkippership, user=user, skippership=skippership)

        self.client.force_login(user)
        response = self.client.get(reverse("home:schippers"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Kielboot")

    def test_schippers_page_shows_only_the_furthest_child_in_a_chain(self):
        """Users are listed under the deepest skippership in a parent chain."""
        user = G(get_user_model())
        first = G(Skippership, name="KB1")
        second = G(Skippership, name="KB2", parent=first)
        third = G(Skippership, name="KB3", parent=second)
        G(UserSkippership, user=user, skippership=first)
        G(UserSkippership, user=user, skippership=second)
        G(UserSkippership, user=user, skippership=third)

        self.client.force_login(user)
        response = self.client.get(reverse("home:schippers"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "KB3")
        self.assertNotContains(response, "KB1")
        self.assertNotContains(response, "KB2")

    def test_schippers_page_truncates_extended_display_names(self):
        """Long generated names stay within a safe display length in compact lists."""
        long_first_name = "A" * 50
        long_last_name = "B" * 50
        user = G(
            get_user_model(),
            first_name=long_first_name,
            last_name=long_last_name,
            display_name_preference=0,
        )
        skippership = G(Skippership, name="KB1")
        G(UserSkippership, user=user, skippership=skippership)

        self.client.force_login(user)
        response = self.client.get(reverse("home:schippers"))

        self.assertEqual(response.status_code, 200)
        self.assertLessEqual(len(user.display_name), 64)
        self.assertContains(response, user.display_name)


class SchippersMembershipFilterTestCase(TestCase):
    """The skippers page filters by membership; alumni are hidden by default."""

    def setUp(self):
        self.skippership = G(Skippership, name="Kielboot 1")
        self.viewer = G(get_user_model(), first_name="Kijker", last_name="Lid")
        self.client.force_login(self.viewer)

    def skipper(self, first_name, membership_type=None, **membership):
        user = G(get_user_model(), first_name=first_name, last_name="Zeiler")
        G(UserSkippership, user=user, skippership=self.skippership)
        if membership_type is not None:
            membership.setdefault("start", date.today() - timedelta(days=365))
            Membership.objects.create(
                member=user, membership_type=membership_type, **membership
            )
        return user

    def kinds(self):
        response = self.client.get(reverse("home:schippers"))
        return {
            entry["user"].first_name: entry["membership"]
            for group in response.context["skippers_by_level"]
            for entry in group["schippers"]
        }

    def test_membership_kinds(self):
        self.skipper("Actief", MembershipTypes.ACTIVE)
        self.skipper("Buitengewoon", MembershipTypes.ACTIVE_EXCEPTIONAL)
        self.skipper("Passief", MembershipTypes.PASSIVE)
        self.skipper("Passiefbg", MembershipTypes.PASSIVE_EXCEPTIONAL)
        self.skipper("Reunist", MembershipTypes.ALUMNUS)
        self.skipper("Onbekend")
        self.assertEqual(
            self.kinds(),
            {
                "Actief": "active",
                "Buitengewoon": "active",
                "Passief": "passive",
                "Passiefbg": "passive",
                "Reunist": "alumnus",
                "Onbekend": "active",
            },
        )

    def test_checkboxes_default_to_active_and_passive(self):
        response = self.client.get(reverse("home:schippers"))
        self.assertEqual(
            [
                (kind, checked)
                for kind, _label, checked in response.context["membership_filters"]
            ],
            [("active", True), ("passive", True), ("alumnus", False)],
        )

    def test_alumni_are_hidden_until_ticked(self):
        self.skipper("Reunist", MembershipTypes.ALUMNUS)
        self.skipper("Passief", MembershipTypes.PASSIVE)
        response = self.client.get(reverse("home:schippers"))
        self.assertContains(response, 'data-filter-membership="alumnus" hidden')
        self.assertContains(response, 'data-filter-membership="passive" >')
        # Alumni don't count as members in the headline.
        self.assertEqual(response.context["skipper_count"], 1)

    def test_only_the_current_membership_counts(self):
        user = self.skipper(
            "Oudlid",
            MembershipTypes.ACTIVE,
            start=date.today() - timedelta(days=800),
            end=date.today() - timedelta(days=1),
        )
        alumnus = Membership.objects.create(
            member=user, membership_type=MembershipTypes.ALUMNUS, start=date.today()
        )
        self.assertEqual(user.current_membership, alumnus)
        self.assertEqual(self.kinds(), {"Oudlid": "alumnus"})

        alumnus.start = date.today() + timedelta(days=30)
        alumnus.save()
        self.assertIsNone(user.current_membership)
        self.assertEqual(self.kinds(), {"Oudlid": "active"})
