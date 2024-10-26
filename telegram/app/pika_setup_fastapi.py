import asyncio
import json
import logging

import aio_pika

from .queue_handler import process_message, process_request_message

logger = logging.getLogger(__name__)

RABBITMQ_HOST = 'rabbitmq'
PAYMENTS_QUEUE = 'PAYMENTS'
DJANGO_DB_QUEUE = 'DJANGO_DB'
RESPONSE_QUEUE = "RESPONSE_QUEUE"
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
    await channel.declare_queue(DJANGO_DB_QUEUE, durable=True)
    logger.info(f"Queue created: {DJANGO_DB_QUEUE}")


async def send_message(message):
    try:
        connection = await connect_to_rabbitmq()
        message_json = json.dumps(message)
        encoded_message = message_json.encode()

        async with connection:
            channel = await connection.channel()
            await create_django_db_queue(channel)
            response_queue = await channel.declare_queue(RESPONSE_QUEUE, durable=True)

            response_future = asyncio.get_event_loop().create_future()

            async def on_response(message: aio_pika.IncomingMessage):
                async with message.process():
                    try:
                        response_body = message.body.decode()
                        response_json = json.loads(response_body)
                    except Exception as e:
                        logger.error(f"Error decoding response: {e}")
                        return

                    processed_result = await process_request_message(response_json)
                    response_future.set_result(processed_result)

            await channel.set_qos(prefetch_count=1)
            await response_queue.consume(on_response)

            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=encoded_message,
                    reply_to=RESPONSE_QUEUE,
                    correlation_id='12345'
                ),
                routing_key=DJANGO_DB_QUEUE
            )
            logger.info(f"Message sent: {encoded_message}")

            response = await response_future
            logger.info("Response received: %s", response)
            return response
    except Exception as e:
        logger.error(f"Error sending message: {e}")


async def callback(message: aio_pika.IncomingMessage):
    async with message.process():
        await process_message(message)


async def start_rabbit_consumer():
    while True:
        try:
            connection = await connect_to_rabbitmq()
            async with connection:
                channel = await connection.channel()
                await channel.set_qos(prefetch_count=1)
                payments_queue = await channel.declare_queue(PAYMENTS_QUEUE, durable=True)

                await payments_queue.consume(callback)
                logger.info("Consumer started, waiting for messages...")
                await asyncio.Future()

        except (aio_pika.exceptions.AMQPConnectionError, aio_pika.exceptions.ChannelClosed):
            logger.error("Connection lost, retrying in 5 seconds...")
            await asyncio.sleep(5)

        except Exception as e:
            logger.error(f"Error in RabbitMQ consumer: {e}")
            await asyncio.sleep(5)
