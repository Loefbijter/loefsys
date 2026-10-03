from datetime import date
from typing import Any

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms import inlineformset_factory
from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.members.admin import UserSkippershipFormSet
from loefsys.members.models import Skippership, UserSkippership
from loefsys.members.skipperships import backfill_required_skipperships


class SkippershipHierarchyTestCase(TestCase):
    """Tests for requiring the parent skippership."""

    def setUp(self):
        self.kb1 = G(Skippership, name="KB1", parent=None)
        self.kb2 = G(Skippership, name="KB2", parent=self.kb1)
        self.kb3 = G(Skippership, name="KB3", parent=self.kb2)
        self.user = G(get_user_model())

    def test_clean_requires_parent(self):
        """A skippership cannot be given without its parent."""
        entry = UserSkippership(user=self.user, skippership=self.kb2)
        with self.assertRaises(ValidationError):
            entry.full_clean()

    def test_clean_allows_with_parent(self):
        """A skippership can be given once the parent is held."""
        G(UserSkippership, user=self.user, skippership=self.kb1)
        UserSkippership(user=self.user, skippership=self.kb2).full_clean()

    def test_clean_allows_root(self):
        """A skippership without parent needs nothing."""
        UserSkippership(user=self.user, skippership=self.kb1).full_clean()

    def test_skippership_cannot_require_itself(self):
        """A parent chain that loops back is rejected."""
        self.kb1.parent = self.kb3
        with self.assertRaises(ValidationError):
            self.kb1.full_clean()

    def test_backfill(self):
        """Missing lower skipperships are added with the earliest date."""
        other = G(get_user_model())
        G(UserSkippership, user=self.user, skippership=self.kb3, since=date(2020, 5, 1))
        G(UserSkippership, user=other, skippership=self.kb2, since=date(2021, 1, 1))
        G(UserSkippership, user=other, skippership=self.kb1, since=date(2019, 1, 1))

        self.assertEqual(
            backfill_required_skipperships(Skippership, UserSkippership), 2
        )
        self.assertEqual(
            set(
                UserSkippership.objects.filter(user=self.user).values_list(
                    "skippership__name", "since"
                )
            ),
            {
                ("KB1", date(2020, 5, 1)),
                ("KB2", date(2020, 5, 1)),
                ("KB3", date(2020, 5, 1)),
            },
        )
        self.assertEqual(UserSkippership.objects.filter(user=other).count(), 2)
        self.assertEqual(
            backfill_required_skipperships(Skippership, UserSkippership), 0
        )


class UserSkippershipFormSetTestCase(TestCase):
    """Tests for adding skipperships through the user admin inline."""

    def setUp(self):
        self.kb1 = G(Skippership, name="KB1", parent=None)
        self.kb2 = G(Skippership, name="KB2", parent=self.kb1)
        self.user = G(get_user_model())
        self.formset_class: Any = inlineformset_factory(
            get_user_model(),
            UserSkippership,
            formset=UserSkippershipFormSet,
            fields=("skippership",),
            extra=2,
        )

    def _formset(self, rows):
        data = {
            "user_skipperships-TOTAL_FORMS": str(len(rows)),
            "user_skipperships-INITIAL_FORMS": "0",
        }
        for i, (skippership, delete) in enumerate(rows):
            data[f"user_skipperships-{i}-skippership"] = str(skippership.pk)
            if delete:
                data[f"user_skipperships-{i}-DELETE"] = "on"
        return self.formset_class(data, instance=self.user)

    def test_parent_in_same_submission(self):
        """A skippership and its parent can be added together."""
        formset = self._formset([(self.kb2, False), (self.kb1, False)])
        self.assertTrue(formset.is_valid(), formset.errors)

    def test_parent_missing(self):
        """A skippership without its parent is rejected."""
        formset = self._formset([(self.kb2, False)])
        self.assertFalse(formset.is_valid())

    def test_parent_deleted_in_same_submission(self):
        """A parent row marked for deletion does not count."""
        formset = self._formset([(self.kb2, False), (self.kb1, True)])
        self.assertFalse(formset.is_valid())
