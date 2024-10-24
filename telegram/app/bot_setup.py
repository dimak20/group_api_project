import os

from telebot.async_telebot import AsyncTeleBot

TOKEN = os.getenv("TELEGRAM_TOKEN", "1234567890:AAAAA1sBBBB4PSjSGFnUiZAR2wwwwWmgExM")

bot = AsyncTeleBot(TOKEN, parse_mode="HTML")
