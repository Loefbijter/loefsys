"""Getting around on desktop and phone. Spec: e2e/specs/navigation.md."""

import re

import pytest
from playwright.sync_api import expect

from e2e.conftest import open_phone_menu, phone_menu_link

MENU_TARGETS = [
    (r"^(Activiteiten|Activities)$", "/events/"),
    (r"^(Reserveringen|Reservations)$", "/reservations/"),
]


@pytest.mark.parametrize(("name", "path"), MENU_TARGETS)
def test_desktop_menu(member_page, live_server, name, path):
    """NAV-1: the desktop header links to the main sections."""
    member_page.goto(live_server.url)
    member_page.get_by_role("navigation").first.get_by_role(
        "link", name=re.compile(name)
    ).first.click()

    expect(member_page).to_have_url(live_server.url + path)


def test_desktop_about_menu(member_page, live_server):
    """NAV-2: the "Over ons" menu opens and lists the association pages."""
    member_page.goto(live_server.url)
    member_page.get_by_role(
        "button", name=re.compile(r"(Over ons|About)", re.I)
    ).click()

    menu = member_page.get_by_role("menu")
    expect(menu).to_be_visible()
    menu.get_by_role(
        "menuitem", name=re.compile(r"(Over de Vereniging|association)", re.I)
    ).click()
    expect(member_page).to_have_url(f"{live_server.url}/association-information/")


@pytest.mark.parametrize(("name", "path"), MENU_TARGETS)
def test_phone_menu(member_phone_page, live_server, name, path):
    """NAV-3: on a phone the menu opens and links to the main sections."""
    page = member_phone_page
    page.goto(live_server.url)
    open_phone_menu(page)
    phone_menu_link(page, re.compile(name)).click()

    expect(page).to_have_url(live_server.url + path)


@pytest.mark.parametrize(
    "path",
    ["/", "/events/", "/reservations/", "/reservations/add/1", "/profiles/profile/"],
)
def test_phone_pages_fit_the_screen(member_phone_page, live_server, path):
    """NAV-4: member pages don't scroll sideways on a phone."""
    page = member_phone_page
    page.goto(live_server.url + path)
    page.wait_for_load_state("load")

    overflow = page.evaluate(
        "() => document.documentElement.scrollWidth"
        " - document.documentElement.clientWidth"
    )
    assert overflow <= 1, f"{path} is {overflow}px wider than the screen"


def test_unknown_page_shows_not_found(member_page, live_server):
    """NAV-5: an unknown address shows a "not found" page."""
    response = member_page.goto(f"{live_server.url}/bestaat-niet/")

    assert response is not None
    assert response.status == 404
