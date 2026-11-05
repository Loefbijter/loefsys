# End-to-end specs

User stories and acceptance criteria for loefsys, written from the point of view of
the people who use it. Every criterion has an ID (for example `EVT-4`) and is checked
by the Playwright test whose docstring starts with that ID, in `e2e/test_<area>.py`.

| Area | Spec | Tests |
| --- | --- | --- |
| Logging in and out | [auth.md](auth.md) | `test_auth.py` |
| Home page | [home.md](home.md) | `test_home.py` |
| Activities and registering | [events.md](events.md) | `test_events.py` |
| Reservations | [reservations.md](reservations.md) | `test_reservations.py` |
| Skippers | [skippers.md](skippers.md) | `test_skippers.py` |
| Profile | [profile.md](profile.md) | `test_profile.py` |
| Navigation, desktop and phone | [navigation.md](navigation.md) | `test_navigation.py` |
| Language | [language.md](language.md) | `test_language.py` |
| Colour theme | [theme.md](theme.md) | `test_theme.py` |
| Admin roles | [admin.md](admin.md) | `test_admin.py` |

## People

All test people are invented. Never use real members' names or details.

- **Member**: Testa Zeilmaker, an ordinary member without permissions.
- **Other member**: Pim Fokkemast.
- **Activity manager**: Ankie Regatta, in the "Activity managers" group with
  permission to manage sailing events.
- **Admin**: Admin Ankerman, a superuser.

## Conventions

- Find elements the way a person would: by role and accessible name, by label, or by
  visible text. Fall back to an `id` only for widgets without a usable name, and note
  why in the test.
- Texts are Dutch by default. Where a test matches on text it also accepts the English
  source string, so the tests keep working after a string is translated or reworded.
- A criterion that describes a known bug is marked `xfail(strict=True)` with the bug
  in the reason. When the bug is fixed the test starts passing, pytest reports it as
  `XPASS(strict)`, and the marker should be removed.
- A criterion for a feature that is still in an open PR skips itself when the feature
  is missing, and names the PR in the skip reason.
