# from asgiref.sync import async_to_sync
# from celery import shared_task
# from django.db.models import F
# from django.utils import timezone
#
# from checkout.models import Checkout
# from notifications.bot import bot
# from notifications.models import NotificationProfile
#
#
# @shared_task
# def send_successful_borrowing(user_id: int, checkout_id: int):
#     borrowing = Checkout.objects.get(id=checkout_id)
#     profile = NotificationProfile.objects.filter(user_id=user_id).first()
#     if profile:
#         async_to_sync(bot.send_message)(
#             profile.chat_id,
#             f"You have borrowed book {borrowing.book.title}. "
#             f"Expected return date: "
#             f"{borrowing.expected_return_date.strftime('%Y-%m-%d')}"
#         )
#
#
# @shared_task
# def send_outdated_borrowings():
#     borrowings = Checkout.objects.filter(
#         F("expected_return_date") < timezone.now(), actual_return_date=None
#     )
#     profiles = {}
#     for borrowing in borrowings:
#         profile = borrowing.user.notification_profile
#         if profile:
#             profiles[profile] = borrowing
#     for profile, borrowing in profiles.items():
#         async_to_sync(bot.send_message)(
#             profile.chat_id,
#             "You have a book debt "
#             f"({borrowing.book.title}."
#             "Expected date to return: "
#             f"{borrowing.expected_return_date.strftime('%Y-%m-%d')}"
#         )
