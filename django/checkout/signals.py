from django.db.models.signals import post_save
from django.dispatch import receiver

from checkout.models import Checkout


@receiver(post_save, sender=Checkout)
def update_book_inventory(sender, instance: Checkout, created: bool, **kwargs) -> None:

    if not instance.actual_return_date:
        book = instance.book
        book.inventory -= 1

        book.save()