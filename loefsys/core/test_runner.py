"""Module defining the test runner for ``manage.py test``."""

from django.test.runner import DiscoverRunner

from loefsys.core.translations import compile_stale_catalogues


class TestRunner(DiscoverRunner):
    """Compile the translations before running the tests."""

    def setup_test_environment(self, **kwargs):
        """Build any missing or outdated ``.mo`` files first."""
        compile_stale_catalogues()
        super().setup_test_environment(**kwargs)
