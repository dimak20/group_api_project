import logging

from celery import shared_task
from django.contrib.auth import get_user_model
from django.db import transaction
from psycopg2._psycopg import IntegrityError

from notifications.models import NotificationProfile

logger = logging.getLogger(__name__)


def unregister_user_by_chat_id(data: dict):
    email = data.get("email")
    chat_id = data.get("chat_id")
    user = get_user_model().objects.filter(email=email).first()
    if user:
        profile = NotificationProfile.objects.filter(user_id=user.id).first()
        if profile:
            if not profile.chat_id == chat_id:
                return {
                    "target": "unregister_user_by_email",
                    "access": False,
                    "user_id": True,
                    "delete": False,
                    "profile": True
                }
            else:
                profile.delete()
                return {
                    "target": "unregister_user_by_email",
                    "access": True,
                    "delete": True,
                    "user_id": True,
                    "profile": True
                }
        else:
            return {
                "target": "unregister_user_by_email",
                "delete": False,
                "user_id": True,
                "profile": False
            }
    else:
        return {
            "target": "unregister_user_by_email",
            "delete": False,
            "user_id": False,
        }


def get_user_id_from_bot(data: dict):
    email = data.get("email")
    chat_id = data.get("chat_id")
    user = get_user_model().objects.filter(email=email).first()
    if user:
        with transaction.atomic():
            profile, created = get_create_profile(user.id, chat_id)
        return {
            "target": "get_user_id",
            "user_id": user.id,
            "created": created
        }
    else:
        return {
            "target": "get_user_id",
            "user_id": None
        }


def get_create_profile(user_id: int, chat_id: int):
    try:
        with transaction.atomic():
            # Используем defaults для chat_id, чтобы применить его только при создании
            profile, created = NotificationProfile.objects.get_or_create(
                user_id=user_id,
                defaults={"chat_id": chat_id}
            )
        return profile, created
    except IntegrityError:
        # Если запись уже существует из-за гонки, просто получаем её
        return NotificationProfile.objects.get(user_id=user_id), False


@shared_task
def process_django_queue_message(data: dict):
    target = data.get("target")
    if target == "get_user_id":
        return get_user_id_from_bot(data)
    if target == "unregister_user_by_email":
        return unregister_user_by_chat_id(data)
    else:
        return {"target": "unknown target"}
