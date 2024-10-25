import json
import logging
import os
import time

import pika

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
QUEUE_TO_SEND = os.getenv('QUEUE_TO_SEND', 'PAYMENTS') # Очередь для отправки в сервис(ы) с уведомлениями

def get_rabbitmq_credentials():
    """Retrieve RabbitMQ credentials from environment variables."""
    user = os.getenv('RABBITMQ_DEFAULT_USER', 'user')
    password = os.getenv('RABBITMQ_DEFAULT_PASS', 'password')
    return pika.PlainCredentials(user, password)


def consume_messages_from_queue(queue_name):
    """Consume messages from the specified RabbitMQ queue."""
    logger.info(f"Starting consumer for queue: {queue_name}")
    credentials = get_rabbitmq_credentials() # Возвращает обьет PlainCredentials который можно вставить в другой обьект ConnectionParametres
    connection_params = pika.ConnectionParameters(
        host='rabbitmq',
        credentials=credentials,
        heartbeat=600
    )

    # Подключение с задержкой
    for i in range(5):
        try:
            connection = pika.BlockingConnection(connection_params) # Требует обьект ConnectionParameters
            break  # Выход из цикла, если подключение успешно
        except pika.exceptions.AMQPConnectionError:
            logger.warning("Waiting for RabbitMQ to start...")
            time.sleep(1)  # Ждем 1 секунду перед повторной попыткой

    try:
        channel = connection.channel() # Соединяет с дефолтным каналом контейнера RabbitMQ
        channel.queue_declare(queue=queue_name, durable=True) # Слушает очередь (чужую)

        def callback(ch, method, properties, body):
            """Функция, указанная в колбеке, когда приходит сообщение из очереди"""
            try:
                message = body.decode('utf-8') # Сначала просто декодируем обьект
                try:
                    # Попытка декодировать JSON
                    message = json.loads(message)
                    logger.info(f"Received JSON message: {message}")
                except json.JSONDecodeError:
                    # Если это не JSON, оставляем как строку
                    logger.info(f"Received plain text message: {message}")
                # TODO: добавить логику обработки

                ch.basic_ack(delivery_tag=method.delivery_tag)  # Подтверждение обработки сообщения
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


def send_message_to_queue(message: dict, queue_name: str = QUEUE_TO_SEND):
    """Send a message to the specified RabbitMQ queue."""
    credentials = get_rabbitmq_credentials()
    connection_params = pika.ConnectionParameters(
        host='rabbitmq',
        credentials=credentials,
        heartbeat=600
    )

    try:
        # Сериализация сообщения в JSON
        message = json.dumps(message)

        # Открытие соединения через контекстный менеджер
        with pika.BlockingConnection(connection_params) as connection:
            channel = connection.channel()
            channel.queue_declare(queue=queue_name, durable=True) #Создает очередь PAYMENTS, в которую отправляем сообщение или подключаемся к существующей

            channel.basic_publish(
                exchange="",
                routing_key=queue_name, #Указывает свою очередь (как продюсер)
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Указывает, что сообщение будет сохранено
                ),
            )
            logger.info(f"Sent message to queue: {queue_name} | Message: {message}")
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
