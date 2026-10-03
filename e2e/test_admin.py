"""Admin roles. Spec: e2e/specs/admin.md.

The activity manager and "Admin" permission tests cover PR #175 and are skipped on
code without it.
"""

import re

import pytest
from django.contrib.auth.models import Group, Permission
from playwright.sync_api import expect

from e2e import factories
from loefsys.events.models.choices import EventCategories
from loefsys.reservations.models.reservation import Reservation

ACTIVITY_MANAGERS = "Activity managers"

# The activity manager group is made by a data migration, which a plain flush
# between live server tests would throw away.
pytestmark = pytest.mark.django_db(serialized_rollback=True)


def admin_log_in(page, base_url, user):
    """Log ``user`` in through the admin login form."""
    page.goto(f"{base_url}/admin/login/?next=/admin/")
    page.locator("#id_username").fill(user.email)
    page.locator("#id_password").fill(factories.PASSWORD)
    page.locator("#login-form [type=submit]").click()
    return page


def requires_pr_175():
    """Skip the test when the activity manager roles from PR #175 aren't there."""
    if not Group.objects.filter(name=ACTIVITY_MANAGERS).exists():
        pytest.skip("Needs the activity manager roles from PR #175")


@pytest.fixture
def activity_manager(db):
    """Return a member in "Activity managers" who may manage sailing events."""
    requires_pr_175()
    user = factories.make_user(
        email="ankie.regatta@example.org", first_name="Ankie", last_name="Regatta"
    )
    factories.add_to_group(user, ACTIVITY_MANAGERS)
    factories.grant_permissions(user, "events.manage_sailing_events")
    return user


def test_member_without_permissions_cannot_use_admin(page, live_server, member):
    """ADM-1: an ordinary member can't log in to the admin."""
    admin_log_in(page, live_server.url, member)

    expect(page).to_have_url(re.compile(r"/admin/login/"))
    expect(page.locator(".errornote")).to_be_visible()


def test_admin_accepts_pending_reservation(page, live_server, superuser, member):
    """ADM-2: an admin accepts a pending reservation from the reservation list."""
    reservation = factories.make_reservation(member, factories.make_room("Testkamer"))
    admin_log_in(page, live_server.url, superuser)

    page.goto(f"{live_server.url}/admin/reservations/reservation/")
    row = page.locator("#result_list tbody tr", has_text="Testkamer")
    row.get_by_role("button", name=re.compile(r"(Accept|Accepteren)", re.I)).click()

    expect(page.locator(".messagelist")).to_be_visible()
    reservation.refresh_from_db()
    assert reservation.request_status == Reservation.RequestStatus.APPROVED


def test_admin_denies_reservation_with_reason(page, live_server, superuser, member):
    """ADM-3: an admin denies a reservation and gives a reason."""
    reservation = factories.make_reservation(member, factories.make_room("Testkamer"))
    admin_log_in(page, live_server.url, superuser)

    page.goto(f"{live_server.url}/admin/reservations/reservation/")
    row = page.locator("#result_list tbody tr", has_text="Testkamer")
    row.get_by_role("link", name=re.compile(r"(Deny|Weigeren)", re.I)).click()
    page.locator("#id_denial_reason").fill("Ruimte is die dag in onderhoud.")
    page.locator(".submit-row [type=submit]").click()

    expect(page).to_have_url(re.compile(r"/admin/reservations/reservation/"))
    reservation.refresh_from_db()
    assert reservation.request_status == Reservation.RequestStatus.DENIED
    assert reservation.denial_reason == "Ruimte is die dag in onderhoud."


def test_activity_manager_sees_only_events(page, live_server, activity_manager):
    """ADM-4: an activity manager gets into the admin and only sees events."""
    admin_log_in(page, live_server.url, activity_manager)

    expect(page).to_have_url(f"{live_server.url}/admin/")
    page.goto(f"{live_server.url}/admin/events/event/")
    sidebar = page.locator("#nav-sidebar")
    expect(sidebar.locator('a[href="/admin/events/event/"]')).to_be_visible()
    expect(sidebar.locator('a[href^="/admin/reservations/"]')).to_have_count(0)
    expect(sidebar.locator('a[href^="/admin/members/"]')).to_have_count(0)


def test_activity_manager_only_picks_own_categories(
    page, live_server, activity_manager
):
    """ADM-5: an activity manager can only create events in their categories."""
    admin_log_in(page, live_server.url, activity_manager)

    page.goto(f"{live_server.url}/admin/events/event/add/")
    options = page.locator("#id_category option").all_inner_texts()

    assert [o.strip() for o in options if o.strip(" -\n")] == [
        str(EventCategories.SAILING.label)
    ]


def test_activity_manager_cannot_open_other_categories(
    page, live_server, activity_manager
):
    """ADM-6: events in other categories are hidden from an activity manager."""
    sailing = factories.make_event("Regatta Testmeer", category=EventCategories.SAILING)
    factories.make_event("Pubquiz Testkroeg", category=EventCategories.LEISURE)
    admin_log_in(page, live_server.url, activity_manager)

    page.goto(f"{live_server.url}/admin/events/event/")

    expect(page.locator("#result_list")).to_contain_text("Regatta Testmeer")
    expect(page.locator("#result_list")).not_to_contain_text("Pubquiz Testkroeg")
    page.get_by_role("link", name="Regatta Testmeer").click()
    expect(page).to_have_url(re.compile(rf"/admin/events/event/{sailing.pk}/change/"))


def test_activity_manager_sees_contact_details_of_registrations(
    page, live_server, activity_manager, member
):
    """ADM-7: an activity manager sees who registered and how to reach them."""
    member.phone_number = "+31612345678"
    member.save()
    event = factories.make_event("Regatta Testmeer", category=EventCategories.SAILING)
    factories.register(event, member)
    admin_log_in(page, live_server.url, activity_manager)

    page.goto(f"{live_server.url}/admin/events/event/{event.pk}/change/")

    registrations = page.locator(".inline-group", has_text=member.email)
    expect(registrations).to_contain_text("Testa Zeilmaker")
    expect(registrations).to_contain_text("+31612345678")
    expect(registrations.locator("input[type=text], select")).to_have_count(0)


def test_activity_manager_cannot_browse_members(page, live_server, activity_manager):
    """ADM-8: an activity manager can't open the member list."""
    admin_log_in(page, live_server.url, activity_manager)

    response = page.goto(f"{live_server.url}/admin/members/user/")

    assert response is not None
    assert response.status == 403


def test_admin_permission_grants_admin_access(page, live_server, member):
    """ADM-9: the "Admin" permission alone lets a member into the admin."""
    if not Permission.objects.filter(codename="access_admin").exists():
        pytest.skip('Needs the "Admin" permission from PR #175')
    factories.grant_permissions(member, "members.access_admin")

    admin_log_in(page, live_server.url, member)

    expect(page).to_have_url(f"{live_server.url}/admin/")
