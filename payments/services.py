from decimal import Decimal

import stripe
from django.urls import reverse
from rest_framework.request import Request

from checkout.models import Checkout
from payments.exceptions import InvalidPeriodError
from payments.models import Payment


def create_checkout_session(checkout_id: int, request: Request, overdue: bool = False):
    checkout = Checkout.objects.filter(id=checkout_id).first()
    if not checkout:
        return None, "Checkout does not exist"

    try:
        billing_period = get_billing_period(checkout, overdue=overdue)
        return create_stripe_checkout_session(billing_period, checkout, request)
    except InvalidPeriodError as e:
        return None, str(e)


def create_stripe_checkout_session(billing_period, checkout, request):
    total_amount = int(
        (Decimal(billing_period) * checkout.book.daily_fee * Decimal("100")).quantize(
            Decimal("1")
        )
    )

    if total_amount <= 0:
        return None, "Invalid amount to pay."

    success_url_base = request.build_absolute_uri(reverse("payments:success-url"))
    success_url = f"{success_url_base}?session_id={{CHECKOUT_SESSION_ID}}"

    cancel_url = request.build_absolute_uri(reverse("payments:cancel-url"))

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[
            {
                "price_data": {
                    "currency": "usd",
                    "product_data": {
                        "name": checkout.book.title,
                    },
                    "unit_amount": total_amount,
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
        payment_type="payment",
        checkout=checkout,
        session_url=checkout_session.url,
        session_id=checkout_session.id,
        total_amount=total_amount,
    )
    return payment, checkout_session.url


def get_billing_period(checkout: Checkout, overdue: bool = False):
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
