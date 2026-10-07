"""Switching language. Spec: e2e/specs/language.md.

Covers PR #172 and is skipped on code without the language switcher.
"""

import re

import pytest
from playwright.sync_api import expect

from e2e.conftest import open_phone_menu

ENGLISH = re.compile(r"^\s*English\s*$")
DUTCH = re.compile(r"^\s*Nederlands\s*$")


def switcher(page, name):
    """Return the language switch button called ``name``, skipping if absent."""
    button = page.get_by_role("button", name=name)
    if button.count() == 0:
        pytest.skip("Needs the language switcher from PR #172")
    return button.filter(visible=True).first


@pytest.fixture
def browser_context_args(browser_context_args):
    """Use an English browser, to check that Dutch is still the default."""
    return {**browser_context_args, "locale": "en-US"}


def test_dutch_is_the_default(member_page, live_server):
    """LANG-1: the site is in Dutch, even for an English browser."""
    member_page.goto(live_server.url)
    switcher(member_page, ENGLISH)

    expect(member_page.locator("html")).to_have_attribute("lang", "nl")
    expect(member_page.get_by_role("link", name="Activiteiten").first).to_be_visible()


def test_switch_to_english_and_back(member_page, live_server):
    """LANG-2 and LANG-3: a member switches to English, it sticks, and back."""
    member_page.goto(f"{live_server.url}/reservations/")
    switcher(member_page, ENGLISH).click()

    expect(member_page).to_have_url(f"{live_server.url}/reservations/")
    expect(member_page.locator("html")).to_have_attribute("lang", "en")
    member_page.goto(f"{live_server.url}/events/")
    expect(member_page.locator("html")).to_have_attribute("lang", "en")

    switcher(member_page, DUTCH).click()
    expect(member_page.locator("html")).to_have_attribute("lang", "nl")


def test_switch_language_on_phone(member_phone_page, live_server):
    """LANG-4: the language switch is reachable from the phone menu."""
    page = member_phone_page
    page.goto(live_server.url)
    open_phone_menu(page)
    switcher(page, ENGLISH).click()

    expect(page.locator("html")).to_have_attribute("lang", "en")
