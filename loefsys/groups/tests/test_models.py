from django.test import TestCase
from django_dynamic_fixture import G

from loefsys.groups.models import (
    Board,
    Committee,
    Fraternity,
    LoefbijterGroup,
    YearClub,
)


class GroupTestCase(TestCase):
    """Tests for Group model creation and validation."""

    def test_create(self):
        """Test that Group instance can be created."""
        generic_group = G(LoefbijterGroup)
        self.assertIsNotNone(generic_group)
        self.assertIsNotNone(generic_group.pk)


class BoardTestCase(TestCase):
    """Tests for Board model creation and validation."""

    def test_create(self):
        """Test that Board instance can be created."""
        board = G(Board)
        self.assertIsNotNone(board)
        self.assertIsNotNone(board.pk)


class CommitteeTestCase(TestCase):
    """Tests for Committee model creation and validation."""

    def test_create(self):
        """Test that Committee instance can be created."""
        committee = G(Committee)
        self.assertIsNotNone(committee)
        self.assertIsNotNone(committee.pk)


class FraternityTestCase(TestCase):
    """Tests for Fraternity model creation and validation."""

    def test_create(self):
        """Test that Fraternity instance can be created."""
        fraternity = G(Fraternity)
        self.assertIsNotNone(fraternity)
        self.assertIsNotNone(fraternity.pk)


class YearClubTestCase(TestCase):
    """Tests for YearClub model creation and validation."""

    def test_create(self):
        """Test that YearClub instance can be created."""
        year_club = G(YearClub)
        self.assertIsNotNone(year_club)
        self.assertIsNotNone(year_club.pk)
