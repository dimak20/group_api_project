from decimal import Decimal

import pyshorteners
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from future.backports.datetime import timedelta

from books.models import Book
from checkout.models import Checkout
from payments.models import Payment, StatusChoices, TypeChoices


class PaymentModelTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@email.com", password="testpass123"
        )
        self.book = Book.objects.create(
            title="Test Book",
            year=2024,
            cover="Hard",
            inventory=1,
            daily_fee=1,
        )
        self.checkout = Checkout.objects.create(
            checkout_date=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=2),
            book = self.book,
            user = self.user

        )
        self.payment = Payment.objects.create(
            status=StatusChoices.PENDING,
            payment_type=TypeChoices.PAYMENT,
            checkout = self.checkout,
            session_url="http://example.com",
            session_id="Test",
            total_amount=Decimal("100")
        )

    def test_pending_payment_str(self):
        self.assertEqual(str(self.payment), f"Status: {self.payment.status}. URL: {self.payment.short_url}.")

    def test_paid_payment_str(self):
        self.payment.status = StatusChoices.PAID
        self.payment.save()
        self.assertEqual(str(self.payment), f"ID: {self.payment.id}. Status: {self.payment.status}.")

    def test_shortened_url(self):
        shortener = pyshorteners.Shortener()
        self.assertEqual(self.payment.short_url, shortener.tinyurl.short(self.payment.session_url))
