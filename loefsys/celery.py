"""Module defining the celery app."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "loefsys.settings")


app = Celery("loefsys")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
