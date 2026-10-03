"""Finding activities and registering for them. Spec: e2e/specs/events.md."""

import re

import pytest
from django.utils import timezone
from playwright.sync_api import expect

from e2e import factories
from e2e.conftest import PHONE, log_in, serve_cdn_from_node_modules
from loefsys.events.models import EventRegistration, RegistrationFormField
from loefsys.events.models.choices import RegistrationStatus

REGISTER = re.compile(r"^\s*(Inschrijven|Register)\s*$", re.I)
CANCEL = re.compile(r"(Afmelden|Cancel|Deregister)", re.I)


def registration_button(page):
    """Return the main register/cancel button on an event page."""
    return page.locator("#registration-button")


def today_at_noon():
    """Return today at 12:00, which the calendar's default week view always shows."""
    return timezone.localtime().replace(hour=12, minute=0, second=0, microsecond=0)


def test_calendar_lists_published_events_only(member_page, live_server):
    """EVT-1: the calendar shows this week's published activities, not drafts."""
    factories.make_event("Zomerregatta Testmeer", start=today_at_noon())
    factories.make_event(
        "Geheime conceptactiviteit", start=today_at_noon(), published=False
    )

    member_page.goto(f"{live_server.url}/events/")

    expect(member_page.get_by_text("Zomerregatta Testmeer")).to_be_visible()
    expect(member_page.get_by_text("Geheime conceptactiviteit")).to_have_count(0)


def test_calendar_event_opens_event_page(member_page, live_server):
    """EVT-2: clicking an activity in the calendar opens its page."""
    event = factories.make_event("Zomerregatta Testmeer", start=today_at_noon())

    member_page.goto(f"{live_server.url}/events/")
    member_page.get_by_text("Zomerregatta Testmeer").click()

    expect(member_page).to_have_url(re.compile(re.escape(event.get_absolute_url())))
    expect(
        member_page.get_by_role("heading", name="Zomerregatta Testmeer", level=1)
    ).to_be_visible()


def test_event_page_shows_details(member_page, live_server):
    """EVT-3: the event page shows when, where and what."""
    event = factories.make_event(
        "Zomerregatta Testmeer",
        location="Jachthaven Verzonnenburg",
        description="Drie races en daarna barbecue.",
    )

    member_page.goto(live_server.url + event.get_absolute_url())

    expect(member_page.get_by_role("heading", level=1)).to_have_text(
        "Zomerregatta Testmeer"
    )
    expect(member_page.get_by_text("Jachthaven Verzonnenburg")).to_be_visible()
    expect(member_page.get_by_text("Drie races en daarna barbecue.")).to_be_visible()


def test_member_registers_and_cancels(member_page, live_server, member):
    """EVT-4 and EVT-5: a member registers for an open activity and cancels again."""
    event = factories.make_event("Zomerregatta Testmeer")
    member_page.goto(live_server.url + event.get_absolute_url())

    expect(registration_button(member_page)).to_have_text(REGISTER)
    registration_button(member_page).click()

    expect(registration_button(member_page)).to_have_text(CANCEL)
    assert EventRegistration.objects.filter(
        event=event, contact=member, status=RegistrationStatus.ACTIVE
    ).exists()

    registration_button(member_page).click()

    expect(registration_button(member_page)).to_have_text(REGISTER)
    assert not EventRegistration.objects.filter(
        event=event, contact=member, status=RegistrationStatus.ACTIVE
    ).exists()


def test_full_event_puts_member_in_queue(member_page, live_server, other_member):
    """EVT-6: registering for a full activity puts the member on the waiting list."""
    event = factories.make_event("Volle kroegentocht", capacity=1)
    factories.register(event, other_member)

    member_page.goto(live_server.url + event.get_absolute_url())
    expect(registration_button(member_page)).to_have_text(
        re.compile(r"(wachtrij|queue|waiting)", re.I)
    )
    registration_button(member_page).click()

    expect(registration_button(member_page)).to_have_text(
        re.compile(r"(Verlaat wachtrij|Leave)", re.I)
    )


def test_registration_not_open_yet(member_page, live_server):
    """EVT-7: before registration opens, the button is disabled and says when."""
    event = factories.make_event("Winterborrel", days_ahead=20, registration_open=False)

    member_page.goto(live_server.url + event.get_absolute_url())

    expect(registration_button(member_page)).to_be_disabled()
    expect(registration_button(member_page)).to_contain_text(
        re.compile(r"(vanaf|from)", re.I)
    )


def test_registration_opening_time_is_local(member_page, live_server):
    """EVT-12: the time registration opens is shown in Dutch time."""
    event = factories.make_event("Winterborrel", days_ahead=20, registration_open=False)
    opens = timezone.localtime(event.registration_start).strftime("%H:%M")

    member_page.goto(live_server.url + event.get_absolute_url())

    expect(registration_button(member_page)).to_contain_text(opens)


@pytest.mark.parametrize("layout", [{}, PHONE], ids=["desktop", "phone"])
def test_times_are_dutch_from_abroad(
    browser, browser_context_args, live_server, member, layout
):
    """EVT-13: times are shown in Dutch time even when the browser is abroad."""
    factories.make_event("Zomerregatta Testmeer", start=today_at_noon())
    event = factories.make_event("Winterborrel", days_ahead=20, registration_open=False)
    opens = timezone.localtime(event.registration_start).strftime("%H:%M")
    context = browser.new_context(
        **{**browser_context_args, **layout, "timezone_id": "Europe/Athens"}
    )
    page = context.new_page()
    serve_cdn_from_node_modules(page)
    log_in(page, live_server.url, member)

    page.goto(f"{live_server.url}/events/")
    expect(
        page.locator("#calendar").get_by_text("12:00").filter(visible=True).first
    ).to_be_visible()

    page.goto(live_server.url + event.get_absolute_url())
    expect(registration_button(page)).to_contain_text(opens)
    context.close()


def test_unpublished_event_is_not_found(member_page, live_server):
    """EVT-8: a draft activity cannot be opened by members."""
    event = factories.make_event("Geheime conceptactiviteit", published=False)

    response = member_page.goto(live_server.url + event.get_absolute_url())

    assert response is not None
    assert response.status == 404


def test_registration_with_extra_questions(member_page, live_server, member):
    """EVT-9: an activity with extra questions asks them before registering."""
    event = factories.make_event("Zeilweekend Testeiland")
    RegistrationFormField.objects.create(
        event=event,
        type=RegistrationFormField.TEXT_FIELD,
        subject="Dieetwensen",
        required=True,
    )
    member_page.goto(live_server.url + event.get_absolute_url())

    registration_button(member_page).click()
    member_page.get_by_label("Dieetwensen").fill("Geen pinda's")
    member_page.locator("#registration-modal").get_by_role(
        "button", name=REGISTER
    ).click()

    expect(registration_button(member_page)).to_have_text(CANCEL)
    registration = EventRegistration.objects.get(event=event, contact=member)
    assert registration.status == RegistrationStatus.ACTIVE


def test_organizer_sees_their_events_and_attendees(
    member_page, live_server, member, other_member
):
    """EVT-10: an organizer finds their activities under "Mijn events"."""
    event = factories.make_event("Klusdag Testhaven")
    factories.make_organizer(event, member)
    factories.register(event, other_member)

    member_page.goto(live_server.url)
    member_page.get_by_role(
        "link", name=re.compile(r"(Mijn events|My events)", re.I)
    ).click()
    member_page.get_by_text("Klusdag Testhaven").first.click()

    expect(member_page.get_by_role("heading", name="Klusdag Testhaven")).to_be_visible()
    expect(member_page.get_by_text("Pim Fokkemast").first).to_be_visible()


def test_member_without_organized_events_has_no_my_events_link(
    member_page, live_server
):
    """EVT-11: members who organize nothing don't see "Mijn events"."""
    member_page.goto(live_server.url)

    expect(
        member_page.get_by_role(
            "link", name=re.compile(r"(Mijn events|My events)", re.I)
        )
    ).to_have_count(0)
