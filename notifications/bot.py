from asgiref.sync import sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

from notifications.models import NotificationProfile

TOKEN = settings.TELEGRAM_TOKEN

bot = AsyncTeleBot(TOKEN, parse_mode="HTML")

user_states = {}

REGISTER_EMAIL_STATE = "register_email"

UNREGISTER_EMAIL_STATE = "unregister_email"


@bot.message_handler(commands=["start"])
async def start(message):
    photo = open("logos/library_logo.png", "rb")

    keyboard = [
        [
            InlineKeyboardButton("Help", callback_data="1"),
            InlineKeyboardButton("Register", callback_data="2")
        ],
        [InlineKeyboardButton("Unregister", callback_data="3")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await bot.send_photo(
        chat_id=message.chat.id,
        photo=photo,
        caption="Welcome! Please, choose:",
        reply_markup=reply_markup
    )

    # await bot.send_message(message.chat.id, "Please, choose:", reply_markup=reply_markup)


@bot.callback_query_handler(func=lambda call: True)
async def callback_query(call):
    if call.data == "1":
        await main(call.message)
    elif call.data == "2":
        await start_register_email(call.message)
    elif call.data == "3":
        await start_unregister_email(call.message)


@bot.message_handler(commands=["help"])
async def main(message):
    await bot.send_message(
        message.chat.id,
        f"Hi from library bot! You can use /register command "
        "in order to register your profile in bot. \nOr /unregister in "
        "order to delete your bot notification"
    )


@sync_to_async
def get_user_by_email(email: str) -> get_user_model():
    return get_user_model().objects.filter(email=email).first()


@sync_to_async
def create_notification_profile(
        user: get_user_model(),
        chat_id: int
) -> NotificationProfile:
    return NotificationProfile.objects.create(user=user, chat_id=chat_id)


@sync_to_async
def find_notification_profile(
        user_id: int,
        chat_id: int = None,
        registration: bool = False
) -> NotificationProfile | tuple[NotificationProfile | None, bool]:
    if not chat_id and registration:
        return NotificationProfile.objects.filter(user_id=user_id).first()
    else:
        profile = NotificationProfile.objects.filter(user_id=user_id).first()
        if profile:
            if not profile.chat_id == chat_id:
                return profile, False
            else:
                return profile, True

        return None, False


@sync_to_async
def delete_notification_profile(user_id):
    return NotificationProfile.objects.filter(user_id=user_id).delete()


@bot.message_handler(commands=["register"])
async def start_register_email(message):
    user_states[message.chat.id] = REGISTER_EMAIL_STATE
    await bot.send_message(message.chat.id, "Enter your email:")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == REGISTER_EMAIL_STATE)
async def process_register_email(message):
    email = message.text
    user = await get_user_by_email(email)

    if not user:
        await bot.send_message(message.chat.id, "Please, enter an existing email")
    else:
        profile = await find_notification_profile(user_id=user.id, registration=True)
        if profile:
            await bot.send_message(message.chat.id, "You have already registered!")
        else:
            await create_notification_profile(user=user, chat_id=message.chat.id)
            await bot.send_message(message.chat.id, "Done!")

        user_states.pop(message.chat.id, None)


@bot.message_handler(commands=["unregister"])
async def start_unregister_email(message):
    user_states[message.chat.id] = UNREGISTER_EMAIL_STATE
    await bot.send_message(message.chat.id, "Enter your email:")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == UNREGISTER_EMAIL_STATE)
async def unregister_user(message):
    email = message.text

    user = await get_user_by_email(email)
    if not user:
        await bot.send_message(
            message.chat.id,
            "Please, enter an existing email"
        )
    else:
        profile, access = await find_notification_profile(user_id=user.id, chat_id=message.chat.id)
        if profile and access:
            await delete_notification_profile(user_id=user.id)
            await bot.send_message(
                message.chat.id,
                "Your profile has been successfully deleted!"
            )
        elif profile and not access:
            await bot.send_message(
                message.chat.id,
                "This email is not associated with your account."
            )
        else:
            await bot.send_message(
                message.chat.id,
                "No profile with this email"
            )

        user_states.pop(message.chat.id, None)


@bot.message_handler()
async def info(message):
    if message.text.lower() == "hi":
        await bot.send_message(message.chat.id, f"Hi, {message.from_user.first_name}")


async def send_message_to_user(profile: NotificationProfile, text: str):
    await bot.send_message(profile.chat_id, text)
