"""Django app for reservations.

In this app, reservations are defined.
"""


def load_tests(loader, _tests, pattern):
    """Load tests if the reservations module is loaded.

    This function hooks into the unittest discovery process
    and only adds the loefsys.reservations tests if it is included in
    INSTALLED_APPS. This prevents unnecessary errors when testing.
    """
    from os.path import abspath, dirname

    from django.apps import apps

    if apps.is_installed("loefsys.reservations"):
        if pattern is None:
            pattern = "test*.py"
        return loader.discover(start_dir=dirname(abspath(__file__)), pattern=pattern)
