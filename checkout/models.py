from django.db import models
from django.db.models import DO_NOTHING


class Checkout(models.Model):
    checkout_date = models.DateTimeField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField()
    book = models.ForeignKey(Book, on_delete=DO_NOTHING, related_name="checkouts")
    user = models.ForeignKey(User, on_delete=DO_NOTHING, related_name="checkouts")

    def __str__(self) -> str:
        return (
            f"Expected checkout duration - {self.expected_return_date - self.borrow_date}"
        )
