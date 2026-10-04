"""Switching between light and dark. Spec: e2e/specs/theme.md."""

import re

import pytest
from playwright.sync_api import expect

from e2e.conftest import open_phone_menu

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
