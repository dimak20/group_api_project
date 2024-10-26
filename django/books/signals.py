import os
from django.db.models.signals import pre_delete
from django.dispatch import receiver
from books.models import Book


@receiver(pre_delete, sender=Book)
def delete_image(sender, instance, **kwargs):
    if instance.image:  # Check if an image is associated
        if os.path.isfile(instance.image.path):  # Check if the file exists
            os.remove(instance.image.path)  # Delete the file
