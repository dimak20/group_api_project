import time

from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Wait for the database to be available."  # noqa

    def handle(self, *args, **kwargs):
        db_conn = connections["default"]
        while True:
            try:
                db_conn.ensure_connection()  # Ensure the connection is established
                self.stdout.write(self.style.SUCCESS("Database available!"))
                break
            except OperationalError:
                self.stdout.write(self.style.WARNING("Waiting for database..."))
                time.sleep(1)
