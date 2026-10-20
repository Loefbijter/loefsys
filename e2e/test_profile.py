"""The member's own profile. Spec: e2e/specs/profile.md."""

import re

from playwright.sync_api import expect

from e2e import factories


def open_own_profile(page):
    """Open the member's profile through the profile icon in the header."""
    page.get_by_role(
        "link", name=re.compile(r"(User Profile|Profiel)", re.I)
    ).first.click()


def test_member_sees_own_profile(member_page, live_server, member):
    """PROF-1: the profile shows the member's name, email and skipperships."""
    skipperships = factories.make_skipperships()
    factories.grant_skippership(member, skipperships["kb1"], skipperships["kb2"])

    member_page.goto(live_server.url)
    open_own_profile(member_page)

    expect(member_page).to_have_url(f"{live_server.url}/profiles/profile/")
    expect(member_page.get_by_role("heading", name="Testa Zeilmaker")).to_be_visible()
    expect(member_page.get_by_text(member.email)).to_be_visible()
    expect(member_page.get_by_text("Kielboot 2")).to_be_visible()


def test_member_edits_profile(member_page, live_server, member):
    """PROF-2: a member changes their nickname and phone number."""
    member_page.goto(f"{live_server.url}/profiles/profile/")
    member_page.get_by_role(
        "link", name=re.compile(r"(Profiel bewerken|Edit profile)", re.I)
    ).click()
    member_page.get_by_label(re.compile(r"^\s*(Nickname|Bijnaam)\s*$", re.I)).fill(
        "Stuurboord"
    )
    member_page.get_by_label(
        re.compile(r"^\s*(Phone number|Telefoonnummer)\s*$", re.I)
    ).fill("+31612345678")
    member_page.get_by_role("button", name=re.compile(r"(opslaan|save)", re.I)).click()

    expect(member_page).to_have_url(f"{live_server.url}/profiles/profile/")
    member.refresh_from_db()
    assert member.nickname == "Stuurboord"
    assert str(member.phone_number) == "+31612345678"


def test_invalid_birthday_is_rejected(member_page, live_server, member):
    """PROF-3: an impossible birthday shows an error and saves nothing."""
    member_page.goto(f"{live_server.url}/profiles/profile/edit/")
    birthday = member_page.get_by_label(
        re.compile(r"^\s*(Birthday|Verjaardag)\s*$", re.I)
    )
    birthday.evaluate("el => el.removeAttribute('pattern')")
    birthday.fill("31-02-2001")
    member_page.get_by_role("button", name=re.compile(r"(opslaan|save)", re.I)).click()

    expect(member_page).to_have_url(re.compile(r"/profiles/profile/edit/"))
    member.refresh_from_db()
    assert member.birthday is None


def test_member_sets_new_password(member_page, live_server, member):
    """PROF-4: a member sets a new password and can log in with it."""
    new_password = "Nieuw-Zeil-Wachtwoord-77"
    member_page.goto(f"{live_server.url}/profiles/profile/")
    member_page.get_by_role(
        "link", name=re.compile(r"(Wachtwoord instellen|Set password)", re.I)
    ).click()
    member_page.locator("#id_new_password1").fill(new_password)
    member_page.locator("#id_new_password2").fill(new_password)
    member_page.get_by_role("button", name=re.compile(r"(Opslaan|Save)", re.I)).click()

    expect(member_page).to_have_url(f"{live_server.url}/profiles/profile/")
    member.refresh_from_db()
    assert member.check_password(new_password)


def test_member_views_someone_elses_profile(member_page, live_server, other_member):
    """PROF-5: a member can view another member's public profile but not edit it."""
    member_page.goto(f"{live_server.url}/profiles/profile/{other_member.slug}/")

    expect(member_page.get_by_role("heading", name="Pim Fokkemast")).to_be_visible()
    expect(
        member_page.get_by_role(
            "link", name=re.compile(r"(Profiel bewerken|Edit profile)", re.I)
        )
    ).to_have_count(0)
