from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from telebot.async_telebot import AsyncTeleBot

from notifications.models import NotificationProfile

TOKEN = settings.TELEGRAM_TOKEN

bot = AsyncTeleBot(TOKEN, parse_mode="HTML")


@bot.message_handler(commands=["start", "help"])
async def main(message):
    await bot.send_message(
        message.chat.id,
        f"Hi from library bot! You can use /fetch command + email "
        "in order to register your profile in bot. \nOr /unregister in "
        "order to delete your bot notification"
    )


@sync_to_async
def get_user_by_email(email):
    return get_user_model().objects.filter(email=email).first()


@sync_to_async
def create_notification_profile(user, chat_id):
    return NotificationProfile.objects.create(user=user, chat_id=chat_id)


@sync_to_async
def find_notification_profile(user_id):
    return NotificationProfile.objects.filter(user_id=user_id).first()


@sync_to_async
def delete_notification_profile(user_id):
    return NotificationProfile.objects.filter(user_id=user_id).delete()


@bot.message_handler(commands=["fetch"])
async def fetch_email(message):
    command_parts = message.text.split(" ", 1)

    if len(command_parts) < 2:
        await bot.send_message(
            message.chat.id,
            "Please, enter your email that you used in registration"
        )
        return

    email = command_parts[1]

    user = await get_user_by_email(email)
    if not user:
        await bot.send_message(
            message.chat.id,
            "Please, enter an existing email"
        )
    else:
        profile = await find_notification_profile(user_id=user.id)
        if profile:
            await bot.send_message(
                message.chat.id,
                "You have already registered!"
            )
            return
        else:
            await create_notification_profile(user=user, chat_id=message.chat.id)
            await bot.send_message(
                message.chat.id,
                "Done!"
            )


@bot.message_handler(commands=["unregister"])
async def fetch_email(message):
    command_parts = message.text.split(" ", 1)
    if len(command_parts) < 2:
        await bot.send_message(
            message.chat.id,
            "Please, enter your email that you used in registration"
        )
        return

    email = command_parts[1]

    user = await get_user_by_email(email)
    if not user:
        await bot.send_message(
            message.chat.id,
            "Please, enter an existing email"
        )
    else:
        profile = await find_notification_profile(user_id=user.id)
        if profile:
            await delete_notification_profile(user_id=user.id)
            await bot.send_message(
                message.chat.id,
                "Done!"
            )
            return
        else:
            await bot.send_message(
                message.chat.id,
                "Not profile with this email"
            )


@bot.message_handler()
async def info(message):
    if message.text.lower() == "hi":
        await bot.send_message(message.chat.id, f"Hi, {message.from_user.first_name}")


async def send_message_to_user(profile: NotificationProfile, text: str):
    await bot.send_message(profile.chat_id, text)
