from asgiref.sync import async_to_sync
from celery import shared_task
from django.db.models import F
from django.utils import timezone

from checkout.models import Checkout
from notifications.bot import bot
from notifications.models import NotificationProfile
from payments.models import Payment


@shared_task
def send_successful_checkout(user_id: int, checkout_id: int):
    borrowing = Checkout.objects.get(id=checkout_id)
    profile = NotificationProfile.objects.filter(user_id=user_id).first()
    if profile:
        async_to_sync(bot.send_message)(
            profile.chat_id,
            f"You have borrowed book {borrowing.book.title}. "
            f"Expected return date: "
            f"{borrowing.expected_return_date.strftime('%Y-%m-%d')}"
        )


@shared_task
def send_outdated_checkouts():
    checkouts = Checkout.objects.select_related().filter(
        F("expected_return_date") < timezone.now(), actual_return_date=None
    )

    if not checkouts.exists():
        return "No borrowings overdue today!"

    profiles = {}
    for checkout in checkouts:
        profile = checkout.user.notification_profile
        if profile:
            profiles[profile] = checkout
    for profile, checkout in profiles.items():
        async_to_sync(bot.send_message)(
            profile.chat_id,
            "You have a book debt "
            f"({checkout.book.title}."
            "Expected date to return: "
            f"{checkout.expected_return_date.strftime('%Y-%m-%d')}"
        )

    return f"Outdated checkouts: {checkouts.count()}"


@shared_task
def send_payment_url(payment_id):
    payment = Payment.objects.filter(id=payment_id).first()
    if payment:
        user = payment.checkout.user
        profile = user.notification_profile
        if profile:
            async_to_sync(bot.send_message)(
                profile.chat_id,
                f"Your payment url: {payment.sesstion_url}"
            )
