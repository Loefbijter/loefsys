# End-to-end tests

Browser tests that click through loefsys like a member or an admin would. They use
[pytest-playwright](https://playwright.dev/python/) in Chromium against Django's live
server ([pytest-django](https://pytest-django.readthedocs.io/)), with a fresh test
database per test.

The user stories and acceptance criteria they check are in [specs/](specs/README.md).

## Running

```sh
export DJANGO_SECRET_KEY=django-insecure-loefbijter
export DJANGO_DATABASE_URL=sqlite:///db.sqlite
export DJANGO_DEBUG=false

uv sync --all-extras --dev
uv run manage.py tailwind --minify      # the pages need the built stylesheet
uv run playwright install chromium      # once
uv run pytest e2e
```

Useful options:

- `--headed --slowmo 300` to watch the browser.
- `-k reservations` to run one area.
- `--tracing retain-on-failure --output test-results`, then
  `uv run playwright show-trace test-results/<test>/trace.zip` to step through a
  failure. CI uploads these traces as the `e2e-test-results` artifact.

The unit tests still run with `uv run manage.py test`; Django's test runner doesn't
pick up the `e2e` folder.

### Without access to jsDelivr

The calendar, icons and photo cropper load from cdn.jsdelivr.net. If your machine
can't reach it, install the same packages locally and the tests serve them from
`node_modules` instead:

```sh
npm install --no-save fullcalendar@6.1.17 @fullcalendar/core@6.1.17 \
  bootstrap-icons@1.11.4 cropperjs@1.6.2
```

## Writing tests

- Start from a criterion in `specs/`, give it an ID, and start the test's docstring
  with that ID.
- Make test data with the helpers in `factories.py`. Only use invented names.
- Prefer `get_by_role`, `get_by_label` and `get_by_text` over CSS selectors, so the
  tests survive redesigns. Where text is matched, accept both the Dutch text and the
  English source string.
- Use `member_page` for a logged-in desktop page and `member_phone_page` for a phone.
  The site chooses its phone layout from the user agent, so a small viewport alone is
  not enough.
