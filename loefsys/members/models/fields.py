"""Custom model fields for the members app."""

from django.db import models


class LowercaseEmailField(models.EmailField):
    """Email field that stores and looks up addresses in lowercase.

    Email addresses are case-insensitive in practice, so ``Jan@Example.com`` and
    ``jan@example.com`` are the same account. Lowercasing on the way into the
    database applies to saves and to lookups such as ``filter(email=...)``.
    """

    def get_prep_value(self, value):
        """Lowercase the address before it is saved or used in a lookup."""
        value = super().get_prep_value(value)
        return value.lower() if isinstance(value, str) else value

    def pre_save(self, model_instance, add):
        """Lowercase the address on the instance too, so it matches the database."""
        value = super().pre_save(model_instance, add)
        if isinstance(value, str) and value != value.lower():
            value = value.lower()
            setattr(model_instance, self.attname, value)
        return value

    def to_python(self, value):
        """Lowercase the address when it is cleaned by a form or model."""
        value = super().to_python(value)
        return value.lower() if isinstance(value, str) else value
