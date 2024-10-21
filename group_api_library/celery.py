import os
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "group_api_library.settings")

app = Celery("group_api_library")

app.config_from_object("django.conf:settings", namespace="CELERY")

app.autodiscover_tasks()
