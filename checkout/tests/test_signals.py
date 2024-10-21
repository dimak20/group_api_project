from django.test import TestCase
from django.db.models.signals import post_save
from rest_framework.test import APIClient

from checkout.models import Checkout, Book
from django.contrib.auth import get_user_model
import datetime

User = get_user_model()


class CheckoutSignalTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)
        self.book = Book.objects.create(title="Test Book", inventory=5)
        self.checkout_date = datetime.date.today()
        self.expected_return_date = self.checkout_date + datetime.timedelta(days=7)

    def test_update_book_inventory_signal(self):
        initial_inventory = self.book.inventory
        checkout = Checkout.objects.create(
            user=self.user,
            book=self.book,
            checkout_date=self.checkout_date,
            expected_return_date=self.expected_return_date
        )
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, initial_inventory - 1)

    def test_no_inventory_change_on_return(self):
        checkout = Checkout.objects.create(
            user=self.user,
            book=self.book,
            checkout_date=self.checkout_date,
            expected_return_date=self.expected_return_date
        )
        initial_inventory = self.book.inventory

        checkout.actual_return_date = datetime.date.today()
        checkout.save()

        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, initial_inventory)
