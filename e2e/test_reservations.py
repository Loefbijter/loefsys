"""Reserving boats and rooms. Spec: e2e/specs/reservations.md."""

import re
from datetime import timedelta

from django.utils import timezone
from playwright.sync_api import expect

from e2e import factories
from loefsys.reservations.models.choices import Locations
from loefsys.reservations.models.reservation import Reservation

PENDING = re.compile(r"(In behandeling|Pending)", re.I)


def slot(days_ahead=5, hours=2):
    """Return a start and end for the datetime-local inputs, on the hour."""
    start = (timezone.localtime() + timedelta(days=days_ahead)).replace(
        minute=0, second=0, microsecond=0
    )
    end = start + timedelta(hours=hours)
    return start.strftime("%Y-%m-%dT%H:%M"), end.strftime("%Y-%m-%dT%H:%M")


def fill_reservation_form(page, item_name, start, end):
    """Pick a period and an item on the reservation form and submit it."""
    page.get_by_label(re.compile(r"^\s*(Van|From)\s*$")).fill(start)
    page.get_by_label(re.compile(r"^\s*(Tot|To|Until)\s*$")).fill(end)
    page.locator("#item-grid label", has_text=item_name).click()
    page.get_by_role("button", name=re.compile(r"^\s*(Reserveren|Reserve)\s*$")).click()


def test_member_sees_only_own_reservations(
    member_page, live_server, member, other_member
):
    """RES-1: the reservations page lists the member's own reservations only."""
    room = factories.make_room("Testkamer")
    boat = factories.make_boat("Zwerver")
    factories.make_reservation(member, room)
    factories.make_reservation(other_member, boat, days_ahead=4)

    member_page.goto(live_server.url)
    member_page.get_by_role(
        "link", name=re.compile(r"^(Reserveringen|Reservations)$")
    ).first.click()

    expect(member_page.get_by_role("heading", level=1)).to_have_text(
        re.compile(r"(Mijn reserveringen|My reservations)", re.I)
    )
    expect(
        member_page.get_by_role("link", name=re.compile("Testkamer"))
    ).to_be_visible()
    expect(member_page.get_by_text("Zwerver")).to_have_count(0)


def test_member_reserves_a_room(member_page, live_server, member):
    """RES-2: a member reserves a room; it shows up as pending."""
    factories.make_room("Testkamer", location=Locations.BOARDROOM)
    start, end = slot()

    member_page.goto(f"{live_server.url}/reservations/")
    member_page.get_by_role(
        "link", name=re.compile(r"(Nieuwe reservering|New reservation)", re.I)
    ).click()
    fill_reservation_form(member_page, "Testkamer", start, end)

    expect(member_page).to_have_url(f"{live_server.url}/reservations/")
    card = member_page.get_by_role("link", name=re.compile("Testkamer"))
    expect(card).to_be_visible()
    expect(card).to_contain_text(PENDING)
    assert Reservation.objects.filter(
        user=member, reservable__name="Testkamer"
    ).exists()


def test_member_reserves_on_a_phone(member_phone_page, live_server, member):
    """RES-9: a member can make a reservation on their phone."""
    factories.make_room("Testkamer", location=Locations.BOARDROOM)
    start, end = slot()

    member_phone_page.goto(f"{live_server.url}/reservations/add/{Locations.BOARDROOM}")
    fill_reservation_form(member_phone_page, "Testkamer", start, end)

    expect(member_phone_page).to_have_url(f"{live_server.url}/reservations/")
    assert Reservation.objects.filter(
        user=member, reservable__name="Testkamer"
    ).exists()


def test_member_switches_location(member_page, live_server):
    """RES-3: choosing a location shows the items kept there."""
    factories.make_room("Testkamer", location=Locations.BOARDROOM)
    factories.make_boat("Zwerver", location=Locations.KRAAIJ)

    member_page.goto(f"{live_server.url}/reservations/add/1")
    expect(member_page.locator("#item-grid")).to_contain_text("Testkamer")
    member_page.get_by_role("link", name="Kraaij").click()

    expect(member_page).to_have_url(re.compile(r"/reservations/add/3$"))
    expect(member_page.locator("#item-grid")).to_contain_text("Zwerver")
    expect(member_page.locator("#item-grid")).not_to_contain_text("Testkamer")


def test_boat_needs_a_skipper(member_page, live_server, member):
    """RES-4: reserving a boat asks for a skipper with the right skippership."""
    skipperships = factories.make_skipperships()
    factories.grant_skippership(member, skipperships["kb1"])
    factories.make_boat("Zwerver", requires_skippership=skipperships["kb1"])
    start, end = slot()

    member_page.goto(f"{live_server.url}/reservations/add/{Locations.KRAAIJ}")
    member_page.get_by_label(re.compile(r"^\s*(Van|From)\s*$")).fill(start)
    member_page.get_by_label(re.compile(r"^\s*(Tot|To|Until)\s*$")).fill(end)
    member_page.locator("#item-grid label", has_text="Zwerver").click()

    skipper_section = member_page.locator("#skipper-section")
    expect(skipper_section).to_be_visible()
    member_page.locator("#id_authorized_userskippership").select_option(
        label="Testa Zeilmaker"
    )
    member_page.get_by_role(
        "button", name=re.compile(r"^\s*(Reserveren|Reserve)\s*$")
    ).click()

    expect(member_page).to_have_url(f"{live_server.url}/reservations/")
    reservation = Reservation.objects.get(reservable__name="Zwerver")
    assert reservation.authorized_userskippership == member


def test_overlapping_reservation_is_refused(member_page, live_server, other_member):
    """RES-5: an item that is already reserved for that period can't be reserved."""
    room = factories.make_room("Testkamer", location=Locations.BOARDROOM)
    existing = factories.make_reservation(other_member, room, days_ahead=5)
    start = timezone.localtime(existing.start).strftime("%Y-%m-%dT%H:%M")
    end = timezone.localtime(existing.end).strftime("%Y-%m-%dT%H:%M")

    member_page.goto(f"{live_server.url}/reservations/add/{Locations.BOARDROOM}")
    fill_reservation_form(member_page, "Testkamer", start, end)

    expect(member_page).to_have_url(re.compile(r"/reservations/add/"))
    expect(member_page.locator("main, body").first).to_contain_text(
        re.compile(r"(already exists|bestaat al|al gereserveerd)", re.I)
    )
    assert Reservation.objects.filter(reservable=room).count() == 1


def test_member_deletes_own_reservation(member_page, live_server, member):
    """RES-6: a member deletes their own reservation after confirming."""
    room = factories.make_room("Testkamer")
    reservation = factories.make_reservation(member, room)

    member_page.goto(f"{live_server.url}/reservations/")
    member_page.get_by_role("link", name=re.compile("Testkamer")).click()
    member_page.get_by_role(
        "link", name=re.compile(r"(Verwijder reservering|Delete reservation)", re.I)
    ).click()
    member_page.get_by_role(
        "button", name=re.compile(r"(Verwijder reservering|Delete reservation)", re.I)
    ).click()

    expect(member_page).to_have_url(f"{live_server.url}/reservations/")
    assert not Reservation.objects.filter(pk=reservation.pk).exists()


def test_member_cannot_open_someone_elses_reservation(
    member_page, live_server, other_member
):
    """RES-7: another member's reservation is not found."""
    reservation = factories.make_reservation(other_member, factories.make_room())

    response = member_page.goto(
        f"{live_server.url}/reservations/detail/{reservation.pk}"
    )

    assert response is not None
    assert response.status == 404


def test_member_cannot_delete_someone_elses_reservation(
    member_page, live_server, other_member
):
    """RES-8: another member's reservation can't be deleted."""
    reservation = factories.make_reservation(other_member, factories.make_room())

    response = member_page.goto(
        f"{live_server.url}/reservations/delete/{reservation.pk}"
    )
    if response is not None and response.ok:
        member_page.get_by_role(
            "button", name=re.compile(r"(Verwijder reservering|Delete)", re.I)
        ).click()

    assert Reservation.objects.filter(pk=reservation.pk).exists()
