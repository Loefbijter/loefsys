"""Privacy helpers: pseudonymization utilities for AVG/GDPR compliance.

Contains helpers to pseudonymize user accounts and other personal data in-place
so records can be retained for bookkeeping while removing personal identifiers.
"""

from collections.abc import Iterable

from django.utils.crypto import get_random_string


def pseudonymize_user(user) -> None:
    """Pseudonymize a single User instance in-place.

    - replaces email with a non-routable placeholder
    - clears names, phone, birthday, note, and address references
    - deletes profile picture file if present
    - deactivates account (is_active=False)

    This keeps the DB record and FK relationships intact while removing
    identifying personal data.
    """
    # Unique token so email collisions are avoided
    token = get_random_string(12)
    user.email = f"deleted+{token}@example.invalid"

    # clear commonly sensitive fields if present
    for attr in (
        "first_name",
        "last_name",
        "initials",
        "nickname",
        "phone_number",
        "pod_kb_link",
        "pod_zb_link",
        "note",
    ):
        if hasattr(user, attr):
            try:
                setattr(user, attr, "")
            except Exception:
                pass

    # birthday and address may be nullable
    if hasattr(user, "birthday"):
        try:
            user.birthday = None
        except Exception:
            pass

    if hasattr(user, "address"):
        try:
            user.address = None
        except Exception:
            pass

    # delete picture file if present
    try:
        if getattr(user, "picture", None):
            user.picture.delete(save=False)
    except Exception:
        # best-effort
        pass

    # deactivate account
    try:
        user.is_active = False
    except Exception:
        pass

    # persist changes
    try:
        user.save()
    except Exception:
        # don't raise in bulk operations
        pass


def pseudonymize_users(queryset: Iterable) -> int:
    """Pseudonymize all users in the given queryset.

    Returns the number of users processed.
    """
    count = 0
    for u in queryset:
        pseudonymize_user(u)
        count += 1
    return count
