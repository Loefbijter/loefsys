"""Module containing the tasks for synchronizing services."""

from celery import group, shared_task


@shared_task(ignore_result=True)
def sync_all_services(user_pk: int):
    """Collector task to trigger all synchronization tasks for a user."""
    group(
        sync_rsc.si(user_pk),
        sync_watersportverbond.si(user_pk),
        sync_conscribo.si(user_pk),
    )()


@shared_task(ignore_result=True)
def sync_rsc(user_pk: int):
    """Task that synchronizes the user data with RSC."""
    print(user_pk)


@shared_task(ignore_result=True)
def sync_watersportverbond(user_pk: int):
    """Task that synchronizes the user data with Watersportverbond."""
    print(user_pk)


@shared_task(ignore_result=True)
def sync_conscribo(user_pk: int):
    """Task that synchronizes the user data with Conscribo."""
    print(user_pk)
