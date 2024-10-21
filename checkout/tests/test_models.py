from django.test import TestCase
from rest_framework.test import APIClient

from checkout.models import Checkout
from books.models import Book
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()

class CheckoutModelTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)
        self.book_available = Book.objects.create(title="Available Book", inventory=5)
        self.book_unavailable = Book.objects.create(title="Unavailable Book", inventory=0)
        self.checkout_date = datetime.date.today()
        self.expected_return_date = self.checkout_date + datetime.timedelta(days=7)

    def test_validate_book_with_available_inventory(self):
        try:
            Checkout.validate_book(self.book_available, ValueError)
        except ValueError:
            self.fail("validate_book() raised ValueError unexpectedly for available book!")

    def test_validate_book_with_unavailable_inventory(self):
        with self.assertRaises(ValueError) as context:
            Checkout.validate_book(self.book_unavailable, ValueError)
        self.assertIn("No available copies of this title", str(context.exception))

    def test_validate_return_date_valid(self):
        try:
            Checkout.validate_return_date(self.checkout_date, self.expected_return_date, ValueError)
        except ValueError:
            self.fail(
                "validate_return_date() raised ValueError unexpectedly for valid return date!"
            )

    def test_validate_return_date_invalid(self):
        invalid_return_date = self.checkout_date
        with self.assertRaises(ValueError) as context:
            Checkout.validate_return_date(self.checkout_date, invalid_return_date, ValueError)
        self.assertIn(
            "The return date must be at least one day after the current date", str(context.exception)
        )

    def test_clean_method(self):
        checkout = Checkout(
            user=self.user,
            book=self.book_available,
            checkout_date=self.checkout_date,
            expected_return_date=self.expected_return_date
        )
        try:
            checkout.clean()
        except ValueError:
            self.fail("clean() raised ValueError unexpectedly!")

    def test_clean_method_with_invalid_data(self):
        checkout = Checkout(
            user=self.user,
            book=self.book_unavailable,
            checkout_date=self.checkout_date,
            expected_return_date=self.checkout_date
        )
        with self.assertRaises(ValueError):
            checkout.clean()
