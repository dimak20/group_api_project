import json
import logging
import os

import aio_pika

from .bot_setup import bot

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    ADMIN_CHAT_ID = int(os.getenv("ADMIN_CHAT_ID", "758342560"))
except Exception as e:
    logger.error(f"An error occurred during processing admin chat id: {e}")


async def process_message_target(data: dict):
    if data.get("target") == "successful_checkout":
        await send_successful_checkout_through_bot(data)
    else:
        logger.warning("Unknown target: %s", data.get("target"))


async def send_successful_checkout_through_bot(data: dict):
    chat_id = data.get("chat_id")
    if not chat_id:
        logger.error("chat_id is missing in the message data")
        return  # If there is no id and this is a dictionary, the message does not arrive to the admin

    if data.get("photo"):
        try:
            await bot.send_photo(
                chat_id=chat_id,
                photo=data.get("photo"),
                caption=data.get("caption", "")  # Default value
            )
        except Exception as e:
            logger.error(f"Failed to send photo: {e}")
    else:
        try:
            await bot.send_message(
                chat_id=chat_id,
                text=data.get("text", "")  # Default value
            )
        except Exception as e:
            logger.error(f"Failed to send message: {e}")


async def process_message(message: aio_pika.IncomingMessage):
    try:
        # Decode the message body and try to download it as JSON
        data = json.loads(message.body.decode())
        logger.info(f"Received JSON message: {data}")

        # If this is a dictionary, then we send it to the handler to find out the target
        await process_message_target(data)

    except json.JSONDecodeError:
        # If it's not JSON, treat it like a regular string
        text_message = message.body.decode()
        logger.warning(f"Received non-JSON message: {text_message}")
        await bot.send_message(ADMIN_CHAT_ID, text_message)

    except Exception as e:
        logger.error(f"An error occurred while processing message: {e}")

async def process_request_message(data: dict):
    target = data.get("target")
    if target == "get_user_id":
        return data
    if target == "unregister_user_by_email":
        return data
    else:
        logger.warning("Unknown target: %s", data.get("target"))
        return None
