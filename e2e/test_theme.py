"""Switching between light and dark. Spec: e2e/specs/theme.md."""

import re

import pytest
from playwright.sync_api import expect

from e2e import factories
from e2e.conftest import open_phone_menu
from loefsys.events.models import RegistrationFormField

FOLLOW_DEVICE = re.compile(r"(Thema: volg apparaat|Theme: follow device)")
LIGHT = re.compile(r"(Thema: licht|Theme: light)")
DARK = re.compile(r"(Thema: donker|Theme: dark)")


@pytest.fixture
def browser_context_args(browser_context_args):
    """Use a device set to dark mode."""
    return {**browser_context_args, "color_scheme": "dark"}


def is_dark(page):
    """Whether the page background is dark, judged by its oklch lightness."""
    background = page.evaluate("getComputedStyle(document.body).backgroundColor")
    lightness = float(re.match(r"oklch\(([\d.]+)", background).group(1))
    return lightness < 0.5


def switch(page, name, role="button"):
    """Return the visible theme switch currently called ``name``."""
    return page.get_by_role(role, name=name).filter(visible=True).first


def test_follows_the_device(member_page, live_server):
    """THEME-1: on a dark device the site is dark by default."""
    member_page.goto(live_server.url)

    expect(switch(member_page, FOLLOW_DEVICE)).to_be_visible()
    assert is_dark(member_page)


def test_choose_light_and_it_sticks(member_page, live_server):
    """THEME-2: choosing light overrides the dark device, also on other pages."""
    member_page.goto(live_server.url)
    switch(member_page, FOLLOW_DEVICE).click()

    expect(switch(member_page, LIGHT)).to_be_visible()
    assert not is_dark(member_page)
    member_page.goto(f"{live_server.url}/events/")
    expect(switch(member_page, LIGHT)).to_be_visible()
    assert not is_dark(member_page)


def test_cycle_back_to_the_device(member_page, live_server):
    """THEME-3: the switch goes light, dark, then follows the device again."""
    member_page.goto(live_server.url)
    switch(member_page, FOLLOW_DEVICE).click()
    switch(member_page, LIGHT).click()

    expect(switch(member_page, DARK)).to_be_visible()
    assert is_dark(member_page)
    switch(member_page, DARK).click()
    expect(switch(member_page, FOLLOW_DEVICE)).to_be_visible()
    member_page.reload()
    expect(switch(member_page, FOLLOW_DEVICE)).to_be_visible()


def test_switch_theme_on_phone(member_phone_page, live_server):
    """THEME-4: the theme switch is reachable from the phone menu."""
    page = member_phone_page
    page.goto(live_server.url)
    open_phone_menu(page)
    # In the phone menu the switch is a menu item, like the entries around it.
    switch(page, FOLLOW_DEVICE, role="menuitem").click()

    expect(switch(page, LIGHT, role="menuitem")).to_be_visible()
    assert not is_dark(page)


# Paints the page background or a panel in a light colour, judged by lightness:
# oklch() as computed, rgb() as relative luminance. Transparent ones don't count.
BRIGHT_BOXES = """() => {
  const lightness = (c) => {
    let m = c.match(/^oklch\\(([\\d.]+)[^/]*(?:\\/\\s*([\\d.]+))?\\)/);
    if (m) return [parseFloat(m[1]), m[2] === undefined ? 1 : parseFloat(m[2])];
    m = c.match(/^rgba?\\((\\d+),\\s*(\\d+),\\s*(\\d+)(?:,\\s*([\\d.]+))?\\)/);
    if (!m) return [0, 0];
    const [r, g, b] = [m[1], m[2], m[3]].map((v) => v / 255);
    const luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b;
    return [Math.cbrt(luminance), m[4] === undefined ? 1 : +m[4]];
  };
  return [...document.querySelectorAll("main *")]
    .filter((el) => {
      const [l, alpha] = lightness(getComputedStyle(el).backgroundColor);
      return l > 0.8 && alpha > 0.5 && el.getClientRects().length > 0;
    })
    .map((el) => el.outerHTML.slice(0, 120));
}"""


DARK_MODE_PAGES = {
    "home": "/",
    "agenda": "/events/",
    "my events": "/events/organized/",
    "event feed": "/events/feed",
    "registration form": "/events/{event}/registration/",
    "reservations": "/reservations/",
    "new reservation": "/reservations/add/1",
    "reservation": "/reservations/detail/{reservation}",
    "cancel reservation": "/reservations/delete/{reservation}",
    "logbook": "/reservations/logbook/{trip}",
    "edit profile": "/profiles/profile/edit/",
}


@pytest.mark.parametrize("page_name", DARK_MODE_PAGES)
def test_pages_follow_dark_mode(member_page, live_server, member, page_name):
    """THEME-5: in dark mode, member pages have no light boxes left over."""
    event = factories.make_event("Klusdag Testhaven")
    factories.make_organizer(event, member)
    RegistrationFormField.objects.create(
        event=event, subject="Dieetwensen", type=RegistrationFormField.TEXT_FIELD
    )
    reservation = factories.make_reservation(member, factories.make_room())
    trip = factories.make_reservation(member, factories.make_boat(), days_ahead=-2)
    path = DARK_MODE_PAGES[page_name].format(
        event=event.slug, reservation=reservation.pk, trip=trip.pk
    )

    member_page.goto(live_server.url + path)

    assert member_page.evaluate(BRIGHT_BOXES) == []
