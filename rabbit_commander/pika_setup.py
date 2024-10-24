import os
import time
import pika
import logging


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_rabbitmq_credentials():
    """Retrieve RabbitMQ credentials from environment variables."""
    user = os.getenv('RABBITMQ_DEFAULT_USER', 'user')
    password = os.getenv('RABBITMQ_DEFAULT_PASS', 'password')
    return pika.PlainCredentials(user, password)


def consume_messages_from_queue(queue_name):
    """Consume messages from the specified RabbitMQ queue."""
    logger.info(f"Starting consumer for queue: {queue_name}")
    credentials = get_rabbitmq_credentials()
    connection_params = pika.ConnectionParameters(
        host='rabbitmq',
        credentials=credentials,
        heartbeat=600
    )

    # Подключение с задержкой
    for i in range(5):
        try:
            connection = pika.BlockingConnection(connection_params)
            break  # Выход из цикла, если подключение успешно
        except pika.exceptions.AMQPConnectionError:
            logger.warning("Waiting for RabbitMQ to start...")
            time.sleep(1)  # Ждем 1 секунду перед повторной попыткой

    try:
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        def callback(ch, method, properties, body):
            try:
                logger.info(f"Received {body.decode('utf-8')}")
                # Ваша логика обработки сообщения здесь
                ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждаем обработку сообщения
            except Exception as e:
                logger.error(f"Error processing message: {e}")
                # Сообщение не подтверждается, чтобы RabbitMQ повторно отправил его

        while True:
            method_frame, header_frame, body = channel.basic_get(queue=queue_name)
            if method_frame:
                callback(channel, method_frame, header_frame, body)
            else:
                time.sleep(1)  # Ждем 1 секунду перед следующей проверкой

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
        logger.info(f"Consumer for queue {queue_name} stopped")


def send_message_to_queue(queue_name, message):
    """Send a message to the specified RabbitMQ queue."""
    credentials = get_rabbitmq_credentials()
    connection_params = pika.ConnectionParameters(
        host='rabbitmq',
        credentials=credentials,
        heartbeat=600
    )

    try:
        connection = pika.BlockingConnection(connection_params)
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message,
            properties=pika.BasicProperties(
                delivery_mode=2,  # Указывает, что сообщение будет сохранено
            ),
        )
        logger.info(f"Sent message to queue: {queue_name}")
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
