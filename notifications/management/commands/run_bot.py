import asyncio
import logging

from django.core.management.base import BaseCommand

from notifications.bot import bot


class Command(BaseCommand):
    help = "Launch telegram bot"

    def handle(self, *args, **options):
        logging.info("Starting bot...")
        asyncio.run(start_bot())


async def start_bot():
    await bot.polling(none_stop=True)
