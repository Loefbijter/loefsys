Translations
============

All strings in code and templates are written in English and wrapped for translation
(``{% translate %}``/``{% blocktranslate trimmed %}`` in templates, ``gettext``/``gettext_lazy``
in Python). Dutch is the default language; English is shown only when a user picks it with
the language switcher.

After adding or changing strings, update and compile the Dutch catalogue (needs GNU gettext)::

    python manage.py makemessages -l nl --add-location file --no-obsolete -i node_modules
    # fill in the new msgstr entries in locale/nl/LC_MESSAGES/django.po
    python manage.py compilemessages

Commit both ``django.po`` and ``django.mo``. CI fails when the catalogue is out of date,
has untranslated or fuzzy entries, or when ``django.mo`` does not match ``django.po``.
