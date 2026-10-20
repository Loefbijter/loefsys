# Navigation, desktop and phone

The site picks its phone layout from the browser's user agent, so phone tests use a
phone-sized viewport with a mobile user agent (`phone_page` in `conftest.py`).

**As a member on a computer, I want a header that takes me to every section.**

- **NAV-1** The header links to Activiteiten and Reserveringen.
- **NAV-2** "Over ons" opens a menu with the association pages.

**As a member on my phone, I want the same sections, in a layout that fits.**

- **NAV-3** The phone menu opens and links to Activiteiten and Reserveringen.
- **NAV-4** The home, calendar, reservations, new reservation and profile pages don't
  scroll sideways on a 412 px wide screen.

**As anyone, I want a clear message when a page doesn't exist.**

- **NAV-5** An unknown address answers "not found" (404).
