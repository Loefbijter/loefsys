"""Category-scoped permissions for managing events.

Every :class:`~loefsys.events.models.choices.EventCategories` value has its own
permission, ``events.manage_<category>_events``. A user can only create and manage
events in the categories they hold this permission for. The permissions can be
granted to Django groups and Loefbijter groups (such as committees) alike.
"""

from .models.choices import EventCategories

ACTIVITY_MANAGERS_GROUP = "Activity managers"
"""Name of the preset group with the base permissions for managing events."""


def allowed_categories(user) -> list[EventCategories]:
    """Return the event categories that ``user`` may create and manage."""
    return [
        category
        for category in EventCategories
        if user.has_perm(f"events.{category.permission_codename}")
    ]
