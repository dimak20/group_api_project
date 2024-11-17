import logging
import os

import httpx
from asgiref.sync import async_to_sync
from celery import shared_task
from django.db.models import F
from django.utils import timezone

from books.models import Book
from checkout.models import Checkout
from notifications.bot import bot
from notifications.email_utils import send_email
from notifications.models import NotificationProfile
from payments.models import Payment
from rabbit_commander.pika_setup import send_message_to_queue

logger = logging.getLogger(__name__)


async def send_message(chat_id, text):
    async with httpx.AsyncClient() as client:
        await client.post(
            f"http://{os.getenv('FAST_API_DOMAIN')}:{os.getenv('FAST_API_PORT')}/send/",
            json={"chat_id": chat_id, "text": text}
        )

@shared_task
def send_successful_checkout(user_id: int, checkout_id: int):
    borrowing = Checkout.objects.get(id=checkout_id)
    profile = NotificationProfile.objects.filter(user_id=user_id).first()
    if profile:
        if not borrowing.book.image:
            message = dict(
                text=f"You have borrowed book {borrowing.book.title}. "
                f"Expected return date: "
                f"{borrowing.expected_return_date.strftime('%Y-%m-%d')}",
                chat_id=profile.chat_id
            )


        else:
            message = dict(
                photo=borrowing.book.image.url,
                caption=(
                    f"You have borrowed the book '{borrowing.book.title}'.\n"
                    f"Expected return date: {borrowing.expected_return_date.strftime('%Y-%m-%d')}"
                ),
                chat_id=profile.chat_id
            )

        message["target"] = "successful_checkout"

        send_message_to_queue(message=message) # Отправляем словарь, сериализация в json на стороне pika_setup



# @shared_task
# def send_successful_checkout(user_id: int, checkout_id: int):
#     async def notify_user_no_photo(chat_id: int, text_data: str):
#         async with httpx.AsyncClient() as client:
#             url = f"http://{os.getenv('FAST_API_DOMAIN')}:{os.getenv('FAST_API_PORT')}/send/"
#             data = {"chat_id": chat_id, "text": text_data}
#             response = await client.post(url, json=data)
#             return response
#
#     async def notify_user_photo(chat_id: int, photo_data: dict):
#         async with httpx.AsyncClient() as client:
#             url = f"http://{os.getenv('FAST_API_DOMAIN')}:{os.getenv('FAST_API_PORT')}/send/"
#             data = {
#                 "chat_id": chat_id,
#                 "photo": {
#                     "photo": photo_data["photo"],
#                     "caption": photo_data.get("caption")
#                 }
#             }
#             response = await client.post(url, json=data)
#             return response
#
#     borrowing = Checkout.objects.get(id=checkout_id)
#     profile = NotificationProfile.objects.filter(user_id=user_id).first()
#     if profile:
#         if not borrowing.book.image:
#             text = (
#                 f"You have borrowed book {borrowing.book.title}. "
#                 f"Expected return date: "
#                 f"{borrowing.expected_return_date.strftime('%Y-%m-%d')}"
#             )
#
#             async_to_sync(notify_user_no_photo)(
#                 profile.chat_id, text
#             )
#
#         else:
#             photo = dict(
#                 photo=borrowing.book.image.url,
#                 caption=(
#                     f"You have borrowed the book '{borrowing.book.title}'.\n"
#                     f"Expected return date: {borrowing.expected_return_date.strftime('%Y-%m-%d')}"
#                 )
#             )
#             async_to_sync(notify_user_photo)(
#                 profile.chat_id, photo
#             )


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
            async_to_sync(send_message)(
                profile.chat_id,
                f"Your payment url: {payment.sesstion_url}"
            )


@shared_task
def create_success_email(checkout_id: int):
    checkout = Checkout.objects.filter(id=checkout_id).first()
    if checkout:
        user = checkout.user
        try:
            subject = "Reminder about your checkout"
            message_content = (
                f"Thanks for borrowing book {checkout.book.title}! <br>"
                f"Expected return date: {checkout.expected_return_date}.<br>"
                f"Daily fee: {checkout.book.daily_fee}"
            )
            send_email(subject, message_content, user.email)
        except Exception as e:
            logger.error(f"Error sending email to {user.email}: {e}")


@shared_task
def send_success_payment_url(payment_id: int):
    payment = Payment.objects.filter(id=payment_id).first()
    if payment:
        book = Book.objects.filter(id=payment.checkout.book.id).first()
        profile = NotificationProfile.objects.filter(user_id=payment.checkout.user.id).first()
        if profile:
            async_to_sync(send_message)(
                profile.chat_id,
                f"Your payment was successful! \n"
                f"Book: {book.title}"
            )


@shared_task
def send_bot_message_with_text(user_id: int, text: str):
    profile = NotificationProfile.objects.filter(user_id=user_id).first()

    if profile:
        async_to_sync(send_message)(
            profile.chat_id,
            text
        )