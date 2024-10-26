import asyncio
import os
from concurrent.futures import ThreadPoolExecutor

import uvicorn

from rabbit_commander.management.commands.consume_queue import Command

UVICORN_HOST = os.getenv("UVICORN_HOST", "0.0.0.0")


async def consume_messages():
    rabbit_consume_command = Command()
    loop = asyncio.get_running_loop()
    executor = ThreadPoolExecutor(max_workers=1)

    while True:
        try:
            await loop.run_in_executor(executor, rabbit_consume_command.handle)
        except Exception as e:
            print(f"Error occurred: {e}. Retrying in 5 seconds...")
            await asyncio.sleep(5)


async def run_uvicorn():
    config = uvicorn.Config("group_api_library.asgi:application", host="0.0.0.0", port=8000, reload=True)
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    consumer_task = asyncio.create_task(consume_messages())
    uvicorn_task = asyncio.create_task(run_uvicorn())

    await asyncio.wait([consumer_task, uvicorn_task])


if __name__ == "__main__":
    asyncio.run(main())
