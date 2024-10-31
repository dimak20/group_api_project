from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from books.models import Book
from checkout.models import Checkout
from payments.models import Payment, StatusChoices, TypeChoices


class BasePaymentsViewTests(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.user = get_user_model().objects.create_user(
            email="test@email.com", password="testpass123"
        )
        self.admin = get_user_model().objects.create_superuser(
            email="admin@email.com", password="testpass123"
        )
        self.user_token = RefreshToken.for_user(self.user).access_token
        self.admin_token = RefreshToken.for_user(self.admin).access_token

        self.book = Book.objects.create(
            title="Test Book",
            year=2024,
            cover="Hard",
            inventory=2,
            daily_fee=1,
        )
        self.checkout1 = Checkout.objects.create(
            checkout_date=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=2),
            book=self.book,
            user=self.user
        )
        self.checkout2 = Checkout.objects.create(
            checkout_date=timezone.now(),
            expected_return_date=timezone.now() + timedelta(days=2),
            book=self.book,
            user=self.admin
        )
        self.payment1 = Payment.objects.create(
            status=StatusChoices.PENDING,
            payment_type=TypeChoices.PAYMENT,
            checkout = self.checkout1,
            session_url="http://example.com",
            session_id="Test1",
            total_amount=Decimal("100")
        )
        self.payment2 = Payment.objects.create(
            status=StatusChoices.PENDING,
            payment_type=TypeChoices.PAYMENT,
            checkout = self.checkout2,
            session_url="http://example.com",
            session_id="Test2",
            total_amount=Decimal("100")
        )

    def authenticate(self, token):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")


class AuthenticatedPaymentsViewTests(BasePaymentsViewTests):
    def test_payments_list_as_user(self):
        self.authenticate(self.user_token)
        res = self.client.get(reverse("payments:payment-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get("results")), 1)
        self.assertFalse("user" in res.data["results"][0]["checkout"])


class AdminPaymentsViewTests(BasePaymentsViewTests):
    def test_payments_list_as_admin(self):
        self.authenticate(self.admin_token)
        res = self.client.get(reverse("payments:payment-list"))
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data.get("results")), 2)
        self.assertTrue("user" in res.data["results"][0]["checkout"])


@patch("payments.views.stripe.checkout.Session.retrieve")
class PaymentsSuccessViewTests(BasePaymentsViewTests):
    class PaymentSession:
        def __init__(self):
            self.payment_status = "paid"

    def test_success_changes_payment_status(self, mock_stripe_session):
        mock_stripe_session.return_value = self.PaymentSession()
        self.authenticate(self.user_token)
        url = reverse("payments:success-url")
        res = self.client.get(f"{url}?session_id={self.payment1.session_id}")
        self.payment1.refresh_from_db()
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(self.payment1.status, StatusChoices.PAID)
        mock_stripe_session.assert_called_once_with(self.payment1.session_id)
