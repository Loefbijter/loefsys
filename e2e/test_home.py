"""The home page. Spec: e2e/specs/home.md."""

import re
from datetime import timedelta

import pytest
from django.utils import timezone
from playwright.sync_api import expect

from e2e import factories
from loefsys.home.models import Announcement


def test_home_shows_upcoming_events(member_page, live_server):
    """HOME-1: the home page previews upcoming activities that link to their page."""
    event = factories.make_event("Zomerregatta Testmeer")

    member_page.goto(live_server.url)
    member_page.get_by_role("link", name=re.compile("Zomerregatta Testmeer")).click()

    expect(member_page).to_have_url(re.compile(re.escape(event.get_absolute_url())))


def test_home_shows_own_upcoming_reservations(member_page, live_server, member):
    """HOME-2: the home page lists the member's upcoming reservations."""
    factories.make_reservation(member, factories.make_room("Testkamer"))

    member_page.goto(live_server.url)

    expect(member_page.get_by_text("Testkamer")).to_be_visible()
    member_page.get_by_role(
        "link",
        name=re.compile(
            r"(Beheer reserveringen|Manage reservations|^\s*Alle?s?\b)", re.I
        ),
    ).first.click()
    expect(member_page).to_have_url(f"{live_server.url}/reservations/")


def test_home_shows_current_announcements(member_page, live_server):
    """HOME-3: published announcements are shown while they are current."""
    now = timezone.now()
    Announcement.objects.create(
        title="Steiger dicht",
        content="De steiger is dit weekend dicht voor onderhoud.",
        announcement_start=now - timedelta(days=1),
        announcement_end=now + timedelta(days=1),
        published=True,
    )
    Announcement.objects.create(
        title="Oud bericht",
        content="Dit bericht is verlopen.",
        announcement_start=now - timedelta(days=10),
        announcement_end=now - timedelta(days=5),
        published=True,
    )

    member_page.goto(live_server.url)

    expect(member_page.get_by_text("Steiger dicht")).to_be_visible()
    expect(member_page.get_by_text("Oud bericht")).to_have_count(0)


@pytest.mark.xfail(
    strict=True,
    reason="Known bug: HomeView shows unpublished events to every active member.",
)
def test_home_hides_draft_events(member_page, live_server):
    """HOME-4: draft activities are not shown to members."""
    factories.make_event("Geheime conceptactiviteit", published=False)

    member_page.goto(live_server.url)

    expect(member_page.get_by_text("Geheime conceptactiviteit")).to_have_count(
        0, timeout=2_000
    )
