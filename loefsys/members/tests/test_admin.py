from datetime import date
from io import BytesIO
from typing import Any

from django.contrib.auth import get_user_model
from django.forms import inlineformset_factory
from django.test import TestCase
from django.urls import reverse
from django_dynamic_fixture import G
from openpyxl import load_workbook

from loefsys.members.admin import MembershipFormSet
from loefsys.members.models import Membership
from loefsys.members.models.choices import MembershipTypes


class MembershipInlineTestCase(TestCase):
    """Memberships are edited on the user's admin page without overlapping."""

    def setUp(self):
        self.user = G(get_user_model())
        self.formset_class: Any = inlineformset_factory(
            get_user_model(),
            Membership,
            formset=MembershipFormSet,
            fields=("membership_type", "start", "end"),
            extra=0,
        )

    def _formset(self, rows, existing=()):
        """Build a bound formset: existing memberships first, then new rows."""
        data = {
            "membership_set-TOTAL_FORMS": str(len(existing) + len(rows)),
            "membership_set-INITIAL_FORMS": str(len(existing)),
        }
        all_rows = [(m.pk, *values) for m, values in existing] + [
            (None, *values) for values in rows
        ]
        for i, (pk, membership_type, start, end, *delete) in enumerate(all_rows):
            prefix = f"membership_set-{i}"
            data[f"{prefix}-id"] = pk or ""
            data[f"{prefix}-membership_type"] = str(membership_type)
            data[f"{prefix}-start"] = start.isoformat()
            data[f"{prefix}-end"] = end.isoformat() if end else ""
            if delete and delete[0]:
                data[f"{prefix}-DELETE"] = "on"
        return self.formset_class(data, instance=self.user)

    def test_consecutive_memberships_are_valid(self):
        formset = self._formset(
            [
                (MembershipTypes.ACTIVE, date(2020, 9, 1), date(2024, 8, 31)),
                (MembershipTypes.ALUMNUS, date(2024, 9, 1), None),
            ]
        )
        self.assertTrue(formset.is_valid(), formset.errors)
        formset.save()
        self.assertEqual(self.user.current_membership.membership_type, 4)

    def test_overlapping_rows_are_refused(self):
        formset = self._formset(
            [
                (MembershipTypes.ACTIVE, date(2020, 9, 1), None),
                (MembershipTypes.ALUMNUS, date(2024, 9, 1), None),
            ]
        )
        self.assertFalse(formset.is_valid())
        self.assertTrue(formset.non_form_errors())

    def test_end_existing_and_add_next_in_one_save(self):
        """Ending the open membership and adding the next one isn't an overlap."""
        active = Membership.objects.create(
            member=self.user,
            membership_type=MembershipTypes.ACTIVE,
            start=date(2020, 9, 1),
        )
        formset = self._formset(
            [(MembershipTypes.ALUMNUS, date(2024, 9, 1), None)],
            existing=[
                (active, (MembershipTypes.ACTIVE, date(2020, 9, 1), date(2024, 8, 31)))
            ],
        )
        self.assertTrue(formset.is_valid(), formset.errors)

    def test_deleted_row_doesnt_count(self):
        active = Membership.objects.create(
            member=self.user,
            membership_type=MembershipTypes.ACTIVE,
            start=date(2020, 9, 1),
        )
        formset = self._formset(
            [(MembershipTypes.PASSIVE, date(2021, 1, 1), None)],
            existing=[(active, (MembershipTypes.ACTIVE, date(2020, 9, 1), None, True))],
        )
        self.assertTrue(formset.is_valid(), formset.errors)

    def test_end_before_start_is_refused(self):
        formset = self._formset(
            [(MembershipTypes.ACTIVE, date(2024, 9, 1), date(2024, 1, 1))]
        )
        self.assertFalse(formset.is_valid())
        self.assertIn("end", formset.forms[0].errors)

    def test_user_change_page_shows_memberships(self):
        admin_user = G(get_user_model(), is_superuser=True, is_active=True)
        Membership.objects.create(
            member=self.user,
            membership_type=MembershipTypes.ALUMNUS,
            start=date(2024, 9, 1),
        )
        self.client.force_login(admin_user)
        response = self.client.get(
            reverse("admin:members_user_change", args=[self.user.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="membership_set-0-membership_type"')


class CurrentMembershipFilterTestCase(TestCase):
    """The user list filters on the type of today's membership."""

    def setUp(self):
        admin_user = G(get_user_model(), email="beheer@example.com", is_superuser=True)
        self.client.force_login(admin_user)
        self.make("actief@example.com", MembershipTypes.ACTIVE, date(2023, 9, 1))
        self.make("reunist@example.com", MembershipTypes.ALUMNUS, date(2024, 9, 1))
        # Was active until last year: only the ended membership exists.
        old = self.make("vroeger@example.com", MembershipTypes.ACTIVE, date(2019, 9, 1))
        old.membership_set.update(end=date(2020, 8, 31))

    def make(self, email, membership_type, start):
        user = G(get_user_model(), email=email)
        Membership.objects.create(
            member=user, membership_type=membership_type, start=start
        )
        return user

    def changelist(self, query):
        return self.client.get(reverse("admin:members_user_changelist") + query)

    def test_filter_on_alumnus(self):
        response = self.changelist(f"?membership={MembershipTypes.ALUMNUS.value}")
        self.assertContains(response, "reunist@example.com")
        self.assertNotContains(response, "actief@example.com")
        self.assertNotContains(response, "vroeger@example.com")

    def test_filter_on_no_current_membership(self):
        response = self.changelist("?membership=none")
        self.assertContains(response, "vroeger@example.com")
        self.assertContains(response, "beheer@example.com")
        self.assertNotContains(response, "reunist@example.com")

    def test_list_shows_current_membership(self):
        response = self.changelist("?membership=0")
        self.assertContains(
            response,
            '<td class="field-current_membership_type">Actief lidmaatschap</td>',
            html=True,
        )


class UserNoteHiddenTestCase(TestCase):
    """The board-only note isn't shown or exported in the user admin."""

    def setUp(self):
        self.admin_user = G(get_user_model(), is_superuser=True, is_active=True)
        self.member = G(
            get_user_model(), email="lid@example.com", note="Board-only remark"
        )
        self.client.force_login(self.admin_user)

    def test_change_page_has_no_note(self):
        response = self.client.get(
            reverse("admin:members_user_change", args=[self.member.pk])
        )
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="note"')
        self.assertNotContains(response, "Board-only remark")

    def test_add_page_has_no_note(self):
        response = self.client.get(reverse("admin:members_user_add"))
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'name="note"')

    def test_export_has_no_note(self):
        response = self.client.get(reverse("admin:members_user_export_excel"))
        self.assertEqual(response.status_code, 200)
        sheet = load_workbook(BytesIO(response.content)).active
        values = [str(cell.value) for row in sheet.iter_rows() for cell in row]
        self.assertIn("lid@example.com", values)
        self.assertNotIn("Board-only remark", values)
        self.assertNotIn("Note", values)
