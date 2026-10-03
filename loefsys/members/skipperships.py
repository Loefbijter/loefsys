"""Helpers for the skippership hierarchy."""

from datetime import date


def backfill_required_skipperships(skippership_model, user_skippership_model) -> int:
    """Give every user the skipperships that the ones they hold require.

    A user holding a skippership must also hold its parent, the parent's parent, and
    so on. Missing entries are created with the earliest ``since`` date of the
    skipperships that require them. The model classes are passed in so that data
    migrations can use their historical models.

    Returns
    -------
    int
        The number of user skipperships created.
    """
    parents = dict(skippership_model.objects.values_list("pk", "parent_id"))
    rows = user_skippership_model.objects.values_list(
        "user_id", "skippership_id", "since"
    )
    held = {(user_id, skippership_id): since for user_id, skippership_id, since in rows}
    missing: dict[tuple[int, int], date] = {}
    for (user_id, skippership_id), since in held.items():
        seen = {skippership_id}
        parent_id = parents.get(skippership_id)
        while parent_id is not None and parent_id not in seen:
            seen.add(parent_id)
            key = (user_id, parent_id)
            if key not in held:
                missing[key] = min(since, missing.get(key, since))
            parent_id = parents.get(parent_id)
    user_skippership_model.objects.bulk_create(
        user_skippership_model(
            user_id=user_id, skippership_id=skippership_id, since=since
        )
        for (user_id, skippership_id), since in missing.items()
    )
    return len(missing)
