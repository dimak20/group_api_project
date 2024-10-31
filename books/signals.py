import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from books.models import Book


@receiver(pre_delete, sender=Book)
def delete_image(sender, instance, **kwargs) -> None:
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)
