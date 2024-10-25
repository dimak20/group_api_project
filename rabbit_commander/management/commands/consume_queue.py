import os

from django.core.management.base import BaseCommand

from rabbit_commander.pika_setup import consume_messages_from_queue

QUEUE_TO_CONSUME = os.getenv("QUEUE_TO_CONSUME", "PAYMENTS")


class Command(BaseCommand):
    help = "Consume messages from RabbitMQ queue"

    def handle(self, *args, **kwargs):
        consume_messages_from_queue(QUEUE_TO_CONSUME)
