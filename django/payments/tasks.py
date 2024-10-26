import stripe
from celery import shared_task
from django.conf import settings
from django.db import transaction
from django.utils import timezone

from notifications.tasks import send_bot_message_with_text
from payments.models import StatusChoices, Payment

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


@shared_task
def check_expired_checkout_sessions():
    payments = Payment.objects.filter(
        status=StatusChoices.PENDING,
        created_at__lte=timezone.now() - timezone.timedelta(hours=24),
    )
    expired_sessions = 0

    for payment in payments:
        session = stripe.checkout.Session.retrieve(payment.session_id)
        if session.get("status") == "expired":
            expired_sessions += 1
            with transaction.atomic():
                payment.status = StatusChoices.EXPIRED
                payment.save(update_fields=["status"])

                book = payment.checkout.book
                book.inventory += 1
                book.save(update_fields=["inventory"])

        send_bot_message_with_text(
            payment.checkout.user.id,
            f"Your checkout session for {payment.checkout.book.title} "
            f"has expired and the checkout has been cancelled."
        )

    return f"Number of expired sessions: {expired_sessions}"
