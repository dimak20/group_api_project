import asyncio

import aio_pika

from .bot_setup import bot

RABBITMQ_HOST = 'rabbitmq'
PAYMENTS_QUEUE = 'PAYMENTS'
DJANGO_DB_QUEUE = 'DJANGO_DB'
RABBITMQ_USER = 'user'
RABBITMQ_PASS = 'password'


async def connect_to_rabbitmq():
    return await aio_pika.connect_robust(
        host=RABBITMQ_HOST,
        login=RABBITMQ_USER,
        password=RABBITMQ_PASS,
        heartbeat=60
    )


async def create_django_db_queue(channel):
    # Создаем очередь DJANGO_DB с параметром durable=True
    await channel.declare_queue(DJANGO_DB_QUEUE, durable=True)
    print(f"Queue created: {DJANGO_DB_QUEUE}")


async def send_message(message: str):
    try:
        connection = await connect_to_rabbitmq()
        async with connection:
            channel = await connection.channel()
            await create_django_db_queue(channel)  # Создаем очередь DJANGO_DB
            await channel.default_exchange.publish(
                aio_pika.Message(body=message.encode()),
                routing_key='DJANGO_DB'
            )
            print("Message sent:", message)
    except Exception as e:
        print("Error sending message:", e)


async def callback(message: aio_pika.IncomingMessage):
    async with message.process():
        print(f"Received: {message.body.decode()}")
        await bot.send_message(message.body.decode())


async def start_rabbit_consumer():
    try:
        connection = await connect_to_rabbitmq()
        async with connection:
            channel = await connection.channel()

            # Установите QoS, если нужно
            await channel.set_qos(prefetch_count=1)  # Ограничивает количество необработанных сообщений
            payments_queue = await channel.declare_queue(PAYMENTS_QUEUE, durable=True)

            # Подписка на очередь PAYMENTS
            await payments_queue.consume(callback)
            print("Consumer started, waiting for messages...")
            await asyncio.Future()  # Ожидание сообщений бесконечно
    except Exception as e:
        print("Error in RabbitMQ consumer:", e)
