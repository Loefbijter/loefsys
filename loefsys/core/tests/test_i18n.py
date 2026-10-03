import ast
import gettext
from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import translation
from django_dynamic_fixture import G

PO_FILE = Path(settings.BASE_DIR) / "locale" / "nl" / "LC_MESSAGES" / "django.po"
MO_FILE = PO_FILE.with_suffix(".mo")


def parse_po(path: Path) -> list[dict]:
    """Parse a .po file into a list of entries keyed by their field names."""
    entries: list[dict] = []
    entry: dict = {}
    key = None

    def flush():
        if "msgid" in entry:
            entries.append(dict(entry))
        entry.clear()

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line:
            flush()
            key = None
        elif line.startswith("#,"):
            if "msgid" in entry:
                flush()
            entry["flags"] = {flag.strip() for flag in line[2:].split(",")}
        elif line.startswith("#"):
            continue
        elif line.startswith('"'):
            entry[key] += ast.literal_eval(line)
        else:
            key, value = line.split(" ", 1)
            if key == "msgctxt" and "msgid" in entry:
                flush()
            entry[key] = ast.literal_eval(value)
    flush()
    return [e for e in entries if e["msgid"]]


class LanguageMiddlewareTestCase(TestCase):
    """Dutch is the default for everyone; English only when chosen."""

    def setUp(self):
        self.client.force_login(G(get_user_model()))

    def test_default_is_dutch_regardless_of_browser(self):
        for accept_language in ("en-US,en;q=0.9", "de-DE", ""):
            response = self.client.get("/", HTTP_ACCEPT_LANGUAGE=accept_language)
            self.assertEqual(response.headers["Content-Language"], "nl")

    def test_chosen_language_is_used(self):
        response = self.client.post(
            reverse("set_language"), {"language": "en", "next": "/"}
        )
        self.assertRedirects(response, "/", fetch_redirect_response=False)
        response = self.client.get("/")
        self.assertEqual(response.headers["Content-Language"], "en")

    def test_unsupported_cookie_falls_back_to_dutch(self):
        self.client.cookies[settings.LANGUAGE_COOKIE_NAME] = "de"
        response = self.client.get("/")
        self.assertEqual(response.headers["Content-Language"], "nl")

    def test_anonymous_user_can_switch_language(self):
        self.client.logout()
        response = self.client.post(
            reverse("set_language"), {"language": "en", "next": "/login/"}
        )
        self.assertRedirects(response, "/login/", fetch_redirect_response=False)


class DutchCatalogueTestCase(TestCase):
    """The Dutch catalogue is complete and compiled."""

    def test_every_string_is_translated(self):
        missing = [
            e["msgid"]
            for e in parse_po(PO_FILE)
            if "fuzzy" in e.get("flags", set())
            or not all(v for k, v in e.items() if k.startswith("msgstr"))
        ]
        self.assertEqual(missing, [], "Untranslated or fuzzy entries in django.po")

    def test_compiled_catalogue_matches_po(self):
        with MO_FILE.open("rb") as file:
            # The parsed messages live in the private _catalog attribute, which the
            # typeshed stubs don't declare.
            catalog: dict = vars(gettext.GNUTranslations(file))["_catalog"]
        stale = []
        for e in parse_po(PO_FILE):
            prefix = f"{e['msgctxt']}\x04" if "msgctxt" in e else ""
            msgid = prefix + e["msgid"]
            if "msgid_plural" in e:
                ok = catalog.get((msgid, 0)) == e["msgstr[0]"]
            else:
                ok = catalog.get(msgid) == e["msgstr"]
            if not ok:
                stale.append(e["msgid"])
        self.assertEqual(stale, [], "django.mo is stale; run compilemessages")

    def test_dutch_is_active_by_default(self):
        with translation.override(settings.LANGUAGE_CODE):
            self.assertEqual(translation.gettext("English"), "Engels")
