import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Union

import httpx
import redis
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from telebot.async_telebot import AsyncTeleBot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

TOKEN = os.getenv("TELEGRAM_TOKEN", "1234567890:AAAAA1sBBBB4PSjSGFnUiZAR2wwwwWmgExM")

bot = AsyncTeleBot(TOKEN, parse_mode="HTML")

user_states = {}

headers = {"Host": "localhost"}

REGISTER_EMAIL_STATE = "register_email"

UNREGISTER_EMAIL_STATE = "unregister_email"

redis_client = redis.Redis(host="redis", port=6379, db=0)

pubsub = redis_client.pubsub()
pubsub.subscribe("bot_channel")

async def listen():
    print("Starting to listen for Redis messages...")
    while True:
        message = pubsub.get_message()
        if message and message['type'] == 'message':
            text = message['data'].decode('utf-8')
            chat_id = 758342560
            await bot.send_message(chat_id=chat_id, text=text)
        await asyncio.sleep(0.1)

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



@bot.message_handler(commands=["register"])
async def start_register_email(message):
    user_states[message.chat.id] = REGISTER_EMAIL_STATE
    await bot.send_message(message.chat.id, "Enter your email:")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == REGISTER_EMAIL_STATE)
async def process_register_email(message):
    email = message.text
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://{os.getenv('DJANGO_DOMAIN')}:{os.getenv('DJANGO_PORT')}/api/v1/handlers/get-email/",
            json={"email": email},
            headers=headers
        )
        user_id = response.json().get("user_id")

        if not user_id:
            await bot.send_message(message.chat.id, "Please, enter an existing email")
        else:
            response = await client.post(
                f"http://{os.getenv('DJANGO_DOMAIN')}:{os.getenv('DJANGO_PORT')}/api/v1/handlers/find-create-profile/",
                json={"user_id": user_id, "chat_id": message.chat.id},
                headers=headers
            )
            created = response.json().get("created")
            if created:
                await bot.send_message(message.chat.id, "You have successfully registered!")
            else:
                await bot.send_message(message.chat.id, f"You have already registered")

            user_states.pop(message.chat.id, None)


@bot.message_handler(commands=["unregister"])
async def start_unregister_email(message):
    user_states[message.chat.id] = UNREGISTER_EMAIL_STATE
    await bot.send_message(message.chat.id, "Enter your email:")


@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == UNREGISTER_EMAIL_STATE)
async def unregister_user(message):
    email = message.text
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"http://{os.getenv('DJANGO_DOMAIN')}:{os.getenv('DJANGO_PORT')}/api/v1/handlers/get-email/",
            json={"email": email},
            headers=headers
        )
        user_id = response.json().get("user_id")

        if not user_id:
            await bot.send_message(
                message.chat.id,
                "Please, enter an existing email"
            )
        else:
            response = await client.post(
                f"http://{os.getenv('DJANGO_DOMAIN')}:{os.getenv('DJANGO_PORT')}/api/v1/handlers/find-delete-profile/",
                json={"user_id": user_id, "chat_id": message.chat.id},
                headers=headers
            )
            profile = response.json().get("profile")
            access = response.json().get("access")
            if profile and access:
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
    if message.text.lower() == "незламний":
        async with httpx.AsyncClient() as client:
            result = await client.post(
                f"http://{os.getenv('DJANGO_DOMAIN')}:{os.getenv('DJANGO_PORT')}/api/v1/handlers/test/",
                json={"aaa": "Незламний"},
                headers=headers
            )
            result_data = result.json()
            await bot.send_message(message.chat.id, f"Hi, {result_data['re']}")


async def start_bot():
    await bot.polling(none_stop=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    bot_task = asyncio.create_task(start_bot())
    listen_task = asyncio.create_task(listen())
    try:
        yield
    finally:
        bot_task.cancel()
        listen_task.cancel()
        await bot_task
        await listen_task


app = FastAPI(lifespan=lifespan)


@app.post("/api/v1.0/notifications")
async def send_user_notification_movie(data):
    movie_name = data.name
    price_drop_percentage = data.price
    tg_username = data.tg_username

    message = f"Hello {tg_username}, the movie '{movie_name}' in your cart has a discount of {price_drop_percentage}%!"

    try:
        await bot.send_message(chat_id=tg_username, text=message)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send message: {str(e)}")

    return {"status": "success", "message": "Notification sent"}


class Message(BaseModel):
    chat_id: int
    text: Union[str, None] = None
    photo: Union[dict, None] = None


@app.post("/send/")
async def send_user_notification(message: Message):
    try:
        if not message.photo:
            await bot.send_message(chat_id=message.chat_id, text=message.text)
        elif message.photo:
            await bot.send_photo(
                chat_id=message.chat_id,
                photo=message.photo.get("photo"),
                caption=message.photo.get("caption")
            )

    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to send message: {str(e)}")

    return {"status": "success", "message": "Notification sent"}


async def bot_send_message_console(chat_id: int, text: str):
    await bot.send_message(
        chat_id=chat_id,
        text=text
    )
