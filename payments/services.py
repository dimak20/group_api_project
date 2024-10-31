from decimal import Decimal

import stripe
from django.conf import settings
from django.urls import reverse
from rest_framework.request import Request

from checkout.models import Checkout
from payments.exceptions import InvalidPeriodError
from payments.models import Payment, TypeChoices


def create_checkout_session(
        checkout_id: int,
        request: Request,
        overdue:
        bool = False
) -> tuple[Payment, str] | tuple[None, str]:
    checkout = Checkout.objects.filter(id=checkout_id).first()
    if not checkout:
        return None, "Checkout does not exist"

    try:
        billing_period = get_billing_period(checkout, overdue=overdue)
        return create_stripe_checkout_session(
            billing_period, checkout, request, overdue=overdue
        )
    except InvalidPeriodError as e:
        return None, str(e)


def create_stripe_checkout_session(
    billing_period: int,
    checkout: Checkout,
    request: Request,
    overdue: bool = False
) -> tuple[Payment, str] | tuple[None, str]:
    total_amount = Decimal(billing_period) * checkout.book.daily_fee
    payment_type = TypeChoices.PAYMENT

    if overdue:
        total_amount *= Decimal(settings.OVERDUE_FINE_MULTIPLIER)
        payment_type = TypeChoices.FINE

    if total_amount <= 0:
        return None, "Invalid amount to pay."

    success_url_base = request.build_absolute_uri(reverse("payments:success-url"))
    success_url = f"{success_url_base}?session_id={{CHECKOUT_SESSION_ID}}"

    cancel_url = request.build_absolute_uri(reverse("payment:cancel-url"))

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": checkout.book.title,
                    },
                    "unit_amount": int(total_amount * 100),
                },
                "quantity": 1,
            }
        ],
        mode="payment",
        success_url=success_url,
        cancel_url=cancel_url,
    )

    payment = Payment.objects.create(
        status="pending",
        payment_type=payment_type,
        checkout=checkout,
        session_url=checkout_session.url,
        session_id=checkout_session.id,
        total_amount=total_amount,
    )
    return payment, checkout_session.url


def get_billing_period(checkout: Checkout, overdue: bool = False) -> int | tuple[None, str]:
    if overdue:
        borrow_days_of_overdue = (
            checkout.actual_return_date - checkout.expected_return_date
        ).days
        if borrow_days_of_overdue < 0:
            return None, "Return date cannot be before borrow date."

        return borrow_days_of_overdue

    borrow_duration_days = (checkout.expected_return_date - checkout.checkout_date).days
    if borrow_duration_days < 0:
        raise InvalidPeriodError("Return date cannot be before checkout date.")
    return borrow_duration_days


def create_webhook(request: Request) -> str:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    webhook_url = request.build_absolute_uri(reverse("payments:stripe-webhook"))

    webhook = stripe.WebhookEndpoint.create(
        enabled_events=["charge.successful", "charge.failed"],
        url=webhook_url
    )
    return webhook.get("secret")


def check_webhook_exists(request: Request) -> str:
    stripe.api_key = settings.STRIPE_SECRET_KEY
    webhook_url = request.build_absolute_uri(reverse("payments:stripe-webhook"))
    webhook_id = None

    webhooks = stripe.WebhookEndpoint.list().get("data")
    for webhook in webhooks:
        if webhook.get("url") == webhook_url:
            webhook_id = webhook.get("id")
            break

    if not webhook_id:
        webhook = stripe.WebhookEndpoint.create(
            enabled_events=["charge.successful", "charge.failed"],
            url=webhook_url
        )
        return webhook.get("secret")
