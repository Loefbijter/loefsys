"""Fixtures for the end-to-end tests.

The tests run against Django's live server (``live_server`` from pytest-django) in a
real Chromium, driven by pytest-playwright. See ``e2e/README.md`` for how to run them.
"""

import os
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, Route, expect

from e2e import factories as data
from loefsys.members.models import User

# Playwright's sync API runs an event loop in the test thread, which makes Django
# refuse database access from the test itself ("SynchronousOnlyOperation").
os.environ.setdefault("DJANGO_ALLOW_ASYNC_UNSAFE", "true")

ROOT = Path(__file__).resolve().parent.parent
NODE_MODULES = ROOT / "node_modules"
CDN_PATTERN = re.compile(
    r"https://cdn\.jsdelivr\.net/npm/(@?[^@/]+(?:/[^@/]+)?)(?:@[^/]+)?/(.+)"
)

DESKTOP = {"viewport": {"width": 1280, "height": 800}}
PHONE_USER_AGENT = (
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/141.0.0.0 Mobile Safari/537.36"
)
PHONE = {
    "viewport": {"width": 412, "height": 915},
    "user_agent": PHONE_USER_AGENT,
    "device_scale_factor": 2.625,
    "is_mobile": True,
    "has_touch": True,
}

expect.set_options(timeout=10_000)


@pytest.fixture
def browser_context_args(browser_context_args):
    """Use a desktop viewport and Dutch as the browser language by default."""
    return {**browser_context_args, **DESKTOP, "locale": "nl-NL"}


@pytest.fixture
def phone_page(browser, browser_context_args):
    """Return a page in a phone-sized context with a mobile user agent.

    The site picks its mobile layout from the user agent, so the viewport alone
    is not enough.
    """
    context = browser.new_context(**{**browser_context_args, **PHONE})
    page = context.new_page()
    page.set_default_timeout(10_000)
    _serve_cdn_from_node_modules(page)
    yield page
    context.close()


def _serve_cdn_from_node_modules(page: Page) -> None:
    """Answer jsDelivr requests from ``node_modules`` when the package is there.

    CI fetches from the CDN directly. Locally, or in sandboxes without access to
    jsDelivr, ``npm install --no-save`` the packages listed in ``e2e/README.md`` and
    the tests use those instead.
    """

    def handle(route: Route) -> None:
        match = CDN_PATTERN.match(route.request.url)
        if match:
            package, path = match.groups()
            local = NODE_MODULES / package / path
            if local.is_file():
                route.fulfill(path=local)
                return
        route.continue_()

    page.route(CDN_PATTERN, handle)


@pytest.fixture
def page(page: Page) -> Page:
    """Return pytest-playwright's page, with CDN requests served locally if possible."""
    page.set_default_timeout(10_000)
    _serve_cdn_from_node_modules(page)
    return page


@pytest.fixture
def member(db):
    """Return an ordinary member without any permissions."""
    return data.make_user()


@pytest.fixture
def other_member(db):
    """Return a second ordinary member."""
    return data.make_user(
        email="pim.fokkemast@example.org", first_name="Pim", last_name="Fokkemast"
    )


@pytest.fixture
def superuser(db):
    """Return a superuser who may do everything in the admin."""
    return User.objects.create_superuser(
        email="admin.ankerman@example.org",
        password=data.PASSWORD,
        first_name="Admin",
        last_name="Ankerman",
    )


def log_in(page: Page, base_url: str, user, next_path: str = "/") -> Page:
    """Log ``user`` in through the login form and wait for the redirect."""
    page.goto(f"{base_url}/login/?next={next_path}")
    page.get_by_label(re.compile(r"^E-?mail", re.I)).fill(user.email)
    page.get_by_label(re.compile(r"^(Wachtwoord|Password)", re.I)).fill(data.PASSWORD)
    page.get_by_role("button", name=re.compile(r"^(Log in|Inloggen)$", re.I)).click()
    expect(page).not_to_have_url(re.compile(r"/login/"))
    return page


def open_phone_menu(page: Page) -> None:
    """Open the navigation menu of the phone layout."""
    menu_button = page.get_by_role(
        "button", name=re.compile(r"^(Menu|Toggle navigation)$")
    )
    if menu_button.count():
        menu_button.first.click()
    else:
        # Older layout: a visually hidden checkbox toggled by its label.
        page.get_by_text("Toggle navigation").first.click(force=True)


def phone_menu_link(page: Page, name: re.Pattern):
    """Return the item called ``name`` in the open phone menu."""
    return (
        page.get_by_role("menuitem", name=name)
        .or_(
            page.get_by_role(
                "navigation", name=re.compile("Mobile navigation")
            ).get_by_role("link", name=name)
        )
        .first
    )


@pytest.fixture
def member_page(page, live_server, member):
    """Return a desktop page logged in as :func:`member`."""
    return log_in(page, live_server.url, member)


@pytest.fixture
def member_phone_page(phone_page, live_server, member):
    """Return a phone page logged in as :func:`member`."""
    return log_in(phone_page, live_server.url, member)
