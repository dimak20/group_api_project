
import logging

from celery import shared_task
from django.contrib.auth import get_user_model


logger = logging.getLogger(__name__)

def get_user_id_from_bot(data: dict):
    email = data.get("email")
    user = get_user_model().objects.filter(email=email).first()
    if user:
        return {
            "target": "get_user_id",
            "user_id": user.id
        }
    else:
        return {
            "target": "get_user_id",
            "user_id": None
        }


@shared_task
def process_django_queue_message(data: dict):
    if data.get("target") == "get_user_id":
        return get_user_id_from_bot(data)
    else:
        return {"target": "unknown target"}
