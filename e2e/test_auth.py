"""Logging in and out. Spec: e2e/specs/auth.md."""

import re

from playwright.sync_api import expect

from e2e.conftest import log_in


def test_anonymous_visitor_is_sent_to_login(page, live_server):
    """AUTH-1: pages for members redirect anonymous visitors to the login page."""
    page.goto(f"{live_server.url}/reservations/")

    expect(page).to_have_url(re.compile(r"/login/"))
    expect(page.get_by_role("button", name=re.compile("Log in", re.I))).to_be_visible()


def test_member_logs_in_and_lands_on_requested_page(page, live_server, member):
    """AUTH-2: after logging in the member lands on the page they asked for."""
    log_in(page, live_server.url, member, next_path="/reservations/")

    expect(page).to_have_url(f"{live_server.url}/reservations/")


def test_wrong_password_shows_an_error(page, live_server, member):
    """AUTH-3: a wrong password keeps the visitor on the login page with an error."""
    page.goto(f"{live_server.url}/login/")
    page.get_by_label(re.compile(r"^E-?mail", re.I)).fill(member.email)
    page.get_by_label(re.compile(r"^(Wachtwoord|Password)", re.I)).fill("niet-goed")
    page.get_by_role("button", name=re.compile("Log in", re.I)).click()

    expect(page).to_have_url(re.compile(r"/login/"))
    login_form = page.locator("form").filter(has=page.locator("input[type=password]"))
    expect(login_form).to_contain_text(
        re.compile(r"(correct|juiste|wachtwoord|password)", re.I)
    )


def test_member_logs_out_from_profile(member_page, live_server):
    """AUTH-4: the member can log out from their profile page."""
    page = member_page
    page.goto(f"{live_server.url}/profiles/profile/")
    page.get_by_role("button", name=re.compile(r"(Uitloggen|Log out)", re.I)).click()

    page.goto(f"{live_server.url}/reservations/")
    expect(page).to_have_url(re.compile(r"/login/"))


def test_password_reset_points_to_web_committee(page, live_server):
    """AUTH-5: "forgot password" explains how to get a new password."""
    page.goto(f"{live_server.url}/login/")
    page.get_by_role(
        "link", name=re.compile(r"(Wachtwoord vergeten|Forgot)", re.I)
    ).click()

    expect(page).to_have_url(re.compile(r"/reset-disabled/"))
