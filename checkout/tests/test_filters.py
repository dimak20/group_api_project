import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from books.models import Book
from checkout.models import Checkout

CHECKOUT_URL = "checkouts:checkout-list"
User = get_user_model()

class CheckoutFilterTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="test_password"
        )
        self.client.force_authenticate(self.user)
        self.book = Book.objects.create(title="Test Book", inventory=10)
        self.checkout1 = Checkout.objects.create(
            user=self.user,
            book=self.book,
            checkout_date=datetime.date(2024, 10, 1),
            expected_return_date=datetime.date(2024, 10, 30),
            actual_return_date=None
        )
        self.checkout2 = Checkout.objects.create(
            user=self.user,
            book=self.book,
            checkout_date=datetime.date(2024, 10, 15),
            expected_return_date=datetime.date(2024, 10, 30),
            actual_return_date=datetime.date(2024, 10, 20)
        )

    def test_filter_by_user(self):
        response = self.client.get(reverse(CHECKOUT_URL), {"user": self.user.id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")

    def test_filter_by_book_title(self):
        response = self.client.get(reverse(CHECKOUT_URL), {"book_title": "Test Book"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Book")

    def test_filter_by_exact_checkout_date(self):
        response = self.client.get(reverse(CHECKOUT_URL), {"checkout_date_exact": "2024-10-01"})
        self.assertEqual(response.status_code, 200)

    def test_filter_by_checkout_date_before(self):
        response = self.client.get(reverse(CHECKOUT_URL), {"checkout_date_before": "2024-10-10"})
        self.assertEqual(response.status_code, 200)

    def test_filter_by_checkout_date_after(self):
        response = self.client.get(reverse(CHECKOUT_URL), {"checkout_date_after": "2024-10-10"})
        self.assertEqual(response.status_code, 200)

    def test_filter_only_returned_books(self):
        response = self.client.get(reverse(CHECKOUT_URL), {"is_returned": True})
        self.assertEqual(response.status_code, 200)
