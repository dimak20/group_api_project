import json
import logging
import os
import time

import pika

from rabbit_commander.tasks import process_django_queue_message

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
QUEUE_TO_SEND = os.getenv('QUEUE_TO_SEND', 'PAYMENTS')  # Queue for sending to service(s) with notifications
QUEUE_TO_CONSUME = os.getenv('QUEUE_TO_CONSUME', 'DJANGO_DB_REQUESTS')
QUEUE_TO_RESPOND = os.getenv('QUEUE_TO_RESPOND', 'DJANGO_DB_RESPONSES')


def get_rabbitmq_credentials():
    """Retrieve RabbitMQ credentials from environment variables."""
    user = os.getenv('RABBITMQ_DEFAULT_USER', 'user')
    password = os.getenv('RABBITMQ_DEFAULT_PASS', 'password')
    return pika.PlainCredentials(user, password)


def consume_messages_from_queue():
    """Consume messages from the specified RabbitMQ queue."""
    logger.info(f"Starting consumer for queue: {QUEUE_TO_CONSUME}")
    credentials = get_rabbitmq_credentials()
    connection_params = pika.ConnectionParameters(
        host='rabbitmq',
        credentials=credentials,
        heartbeat=600
    )

    # Delayed connection
    for i in range(5):
        try:
            connection = pika.BlockingConnection(connection_params)
            break
        except pika.exceptions.AMQPConnectionError:
            logger.warning("Waiting for RabbitMQ to start...")
            time.sleep(1)

    try:
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_TO_CONSUME, durable=True)
        channel.queue_declare(queue=QUEUE_TO_RESPOND, durable=True)

        def callback(ch, method, properties, body):
            """Callback function to process messages."""
            logger.info("Callback triggered.")
            try:
                message = body.decode('utf-8')
                logger.info(f"Raw message: {message}")
                try:
                    message = json.loads(message)
                    logger.info(f"Received JSON message: {message}")
                except json.JSONDecodeError:
                    logger.info(f"Received plain text message: {message}")

                # Calling a task and waiting for the result
                response_message = process_django_queue_message.delay(message)
                response_result = response_message.get(timeout=10)  # waiting for the result
                logger.info(f"Processing message: {message}")
                logger.info(
                    f"Response from processing: {response_result}. "
                    f"Sending to {properties.reply_to}"
                )

                # Sending the response back to the queue
                send_message_to_queue(response_result, properties.reply_to, properties.correlation_id)

                ch.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as e:
                logger.error(f"Error processing message: {e}")

        channel.basic_consume(queue=QUEUE_TO_CONSUME, on_message_callback=callback, auto_ack=False)
        logger.info("Waiting for messages...")
        channel.start_consuming()

    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
        logger.info(f"Consumer for queue {QUEUE_TO_CONSUME} stopped")


def send_message_to_queue(message: dict, queue_name: str = QUEUE_TO_SEND, correlation_id: str = None):
    """Send a message to the specified RabbitMQ queue."""
    credentials = get_rabbitmq_credentials()
    connection_params = pika.ConnectionParameters(
        host='rabbitmq',
        credentials=credentials,
        heartbeat=600
    )

    try:
        # Serializing a message to JSON
        message = json.dumps(message)

        # Opening a connection through the context manager
        with pika.BlockingConnection(connection_params) as connection:
            channel = connection.channel()
            channel.queue_declare(
                queue=queue_name,
                durable=True
            )  # Creates a PAYMENTS queue to which we send a message or connect to an existing one

            channel.basic_publish(
                exchange="",
                routing_key=queue_name,  # Indicates turn (as producer)
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2,  # Indicates that the message will be saved
                    correlation_id=correlation_id
                ),
            )
            logger.info(f"Sent message to queue: {queue_name} | Message: {message} | Correlation_id: {correlation_id}")
    except pika.exceptions.AMQPConnectionError as e:
        logger.error(f"Failed to connect to RabbitMQ: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")
    finally:
        if 'connection' in locals() and connection.is_open:
            connection.close()
