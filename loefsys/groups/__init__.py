"""Django app for groups.

In this app, groups and memberships for groups are defined.
"""


def load_tests(loader, _tests, pattern):
    """Load tests if the groups module is loaded.

    This function hooks into the unittest discovery process
    and only adds the loefsys.groups tests if it is included in
    INSTALLED_APPS. This prevents unnecessary errors when testing.
    """
    from os.path import abspath, dirname

    from django.apps import apps

    if apps.is_installed("loefsys.groups"):
        return loader.discover(start_dir=dirname(abspath(__file__)), pattern=pattern)
