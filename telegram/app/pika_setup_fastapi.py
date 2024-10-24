import asyncio
import pika
from pika.exceptions import AMQPConnectionError, AuthenticationError

from .bot_setup import bot

RABBITMQ_HOST = 'rabbitmq'
PAYMENTS_QUEUE = 'PAYMENTS'
DJANGO_DB_QUEUE = 'DJANGO_DB'
RABBITMQ_USER = 'user'
RABBITMQ_PASS = 'password'


connection = None
channel = None


def connect_to_rabbitmq():
    global connection, channel
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASS)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBITMQ_HOST, credentials=credentials)
        )
        channel = connection.channel()

        # Создаем только DJANGO_DB, если ее еще нет
        channel.queue_declare(queue=DJANGO_DB_QUEUE, durable=True)
        print("Connected to RabbitMQ")

    except (AMQPConnectionError, AuthenticationError) as e:
        print("Failed to connect to RabbitMQ:", e)


def send_message(message: str):
    if channel is None or connection is None:
        connect_to_rabbitmq()

    try:
        # Отправка сообщения в джанго
        channel.basic_publish(exchange='', routing_key=DJANGO_DB_QUEUE, body=message)
        print("Message sent:", message)

    except Exception as e:
        print("Failed to send message:", e)


def callback(ch, method, properties, body):
    print(f"Received {body.decode()}")
    asyncio.create_task(bot.send_message(body.decode()))


def start_rabbit_consumer():
    connect_to_rabbitmq()

    # Подключаемся к уже существующей очереди PAYMENTS
    channel.basic_consume(queue=PAYMENTS_QUEUE, on_message_callback=callback, auto_ack=True)
    print('Waiting for messages. To exit press CTRL+C')

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Consumer stopped.")
    finally:
        if connection and connection.is_open:
            connection.close()
