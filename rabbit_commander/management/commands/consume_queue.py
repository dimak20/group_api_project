import time

from django.core.management.base import BaseCommand
from rabbit_commander.pika_setup import consume_messages_from_queue

class Command(BaseCommand):
    help = "Consume messages from RabbitMQ queue"

    def handle(self, *args, **kwargs):
        consume_messages_from_queue("PAYMENTS")
