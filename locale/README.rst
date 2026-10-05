Translations
============

All strings in code and templates are written in English and wrapped for translation
(``{% translate %}``/``{% blocktranslate trimmed %}`` in templates, ``gettext``/``gettext_lazy``
in Python). Dutch is the default language; English is shown only when a user picks it with
the language switcher.

Only the ``.po`` catalogues are in git: they hold the Dutch translations, which are written
by hand and can't be generated. The compiled ``.mo`` files that Django reads are gitignored
and built with ``compilemessages``. Both commands need GNU gettext (``apt install gettext``,
``brew install gettext``).

After cloning or pulling, compile the catalogues so the site shows Dutch::

    uv run manage.py compilemessages

``manage.py check`` and ``runserver`` warn when this is needed. The Docker image, CI and
the tests (``manage.py test`` and the e2e tests) compile them on their own.

After adding or changing strings, update the Dutch catalogue::

    uv run manage.py makemessages
    # fill in the new msgstr entries in locale/nl/LC_MESSAGES/django.po
    uv run manage.py compilemessages

Commit ``django.po``. The project's ``makemessages`` defaults to Dutch, leaves out source
locations, obsolete entries and the creation date, and sorts entries by message id, so the
file only changes when strings do. When two branches conflict in ``django.po``, keep the
entries from both sides and run ``makemessages`` again to tidy up.

CI fails when ``django.po`` is out of date, and the tests fail when it has untranslated or
fuzzy entries.

``djangojs.po`` holds a few Django admin JavaScript strings that Django doesn't translate
yet. It is edited by hand; ``makemessages`` leaves it alone.
