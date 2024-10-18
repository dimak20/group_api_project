from django.db import models
from django.db.models import DO_NOTHING

from books.models import Book
from user.models import User


class Checkout(models.Model):
    checkout_date = models.DateField(auto_now_add=True)
    expected_return_date = models.DateField()
    actual_return_date = models.DateField(null=True, blank=True)
    book = models.ForeignKey(
        Book,
        on_delete=DO_NOTHING,
        related_name="checkouts"
    )
    user = models.ForeignKey(
        User,
        on_delete=DO_NOTHING,
        related_name="checkouts"
    )

    def __str__(self) -> str:
        return (
            f"Expected checkout duration - "
            f"{self.expected_return_date - self.checkout_date}"
        )

    @staticmethod
    def validate_book(book: Book, error_to_response) -> None:
        if book.inventory < 1:
            raise error_to_response(
                {
                    "book inventory": "No available copies of "
                    "this title at the moment. Please choose another book."

                }
            )

    def clean(self):
        self.validate_book(self.book, ValueError)

    def save(
            self,
            *args,
            force_insert=False,
            force_update=False,
            using=None,
            update_fields=None,
    ):
        self.full_clean()
        return (
            super(Checkout, self).save
            (force_insert, force_update, using, update_fields)
        )
