"""The skippers overview. Spec: e2e/specs/skippers.md."""

import re

from playwright.sync_api import expect

from e2e import factories


def test_skippers_grouped_by_highest_skippership(
    member_page, live_server, member, other_member
):
    """SKIP-1: each skipper is listed once, under their highest skippership."""
    skipperships = factories.make_skipperships()
    factories.grant_skippership(member, skipperships["kb1"], skipperships["kb2"])
    factories.grant_skippership(other_member, skipperships["pico"])

    member_page.goto(live_server.url)
    member_page.get_by_role(
        "button", name=re.compile(r"(Over ons|About)", re.I)
    ).click()
    member_page.get_by_role(
        "menuitem", name=re.compile(r"^Schippers$|^Skippers$")
    ).click()

    expect(member_page).to_have_url(f"{live_server.url}/schippers/")
    kb2 = member_page.get_by_role("heading", name="Kielboot 2")
    expect(kb2).to_be_visible()
    expect(
        member_page.get_by_role("heading", name="Kielboot 1", exact=True)
    ).to_have_count(0)
    expect(member_page.get_by_role("heading", name="Pico")).to_be_visible()
    expect(member_page.get_by_text("Testa Zeilmaker")).to_have_count(1)


def test_skipper_profile_link(member_page, live_server, member, other_member):
    """SKIP-2: a skipper's profile can be opened from the overview."""
    skipperships = factories.make_skipperships()
    factories.grant_skippership(other_member, skipperships["kb1"])

    member_page.goto(f"{live_server.url}/schippers/")
    member_page.get_by_role(
        "link", name=re.compile(r"(Bekijk profiel|View profile|Pim Fokkemast)", re.I)
    ).first.click()

    expect(member_page).to_have_url(
        re.compile(rf"/profiles/profile/{other_member.slug}/")
    )
    expect(member_page.get_by_role("heading", name="Pim Fokkemast")).to_be_visible()


def test_skippers_page_needs_login(page, live_server):
    """SKIP-3: the skippers overview is only for logged-in members."""
    page.goto(f"{live_server.url}/schippers/")

    expect(page).to_have_url(re.compile(r"/login/"))
