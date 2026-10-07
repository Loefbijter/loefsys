"""App configuration for the admin, kept free of model imports."""

from django.contrib.admin.apps import AdminConfig


class LoefsysAdminConfig(AdminConfig):
    """Admin app configuration that uses the permission-based admin site."""

    default_site = "loefsys.core.admin_site.LoefsysAdminSite"
