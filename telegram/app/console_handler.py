import asyncio
import sys

from main import bot_send_message_console


async def main(chat_id, message):
    await bot_send_message_console(chat_id, message)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python send_message.py <chat_id> <message>")
        sys.exit(1)

    chat_id = int(sys.argv[1])
    message = sys.argv[2]
    asyncio.run(main(chat_id, message))
