from django.contrib.auth import get_user_model
from django.db import models
from django.db.models import CASCADE


class NotificationProfile(models.Model):
    user = models.OneToOneField(
        get_user_model(),
        on_delete=CASCADE,
        related_name="notification_profile"
    )
    chat_id = models.BigIntegerField(unique=True)
