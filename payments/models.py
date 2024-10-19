from django.db import models
from django.db.models import CASCADE

from checkout.models import Checkout


class StatusChoices(models.TextChoices):
    PENDING = "pending", "Pending"
    PAID = "paid", "Paid"
    EXPIRED = "expired", "Expired"


class TypeChoices(models.TextChoices):
    PAYMENT = "payment", "Payment"
    FINE = "fine", "Fine"


class Payment(models.Model):
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING
    )
    payment_type = models.CharField(
        max_length=20,
        choices=TypeChoices.choices,
        default=TypeChoices.PAYMENT
    )
    checkout = models.ForeignKey(
        Checkout,
        on_delete=CASCADE,
        related_name="payments"
    )
    session_url = models.URLField(max_length=500)
    session_id = models.CharField(max_length=255)
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return (
            f"Status: {self.status}. URL: {self.session_url}."
        )
