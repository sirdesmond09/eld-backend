import time

from django.core.management import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    "django command to wait for database to be available"

    def handle(self, *args, **options):
        """Entry for command to execute"""

        self.stdout.write("waiting for PostgresSQL database to be available")

        db_up = False

        while not db_up:
            try:
                self.check(databases=["default"])
                db_up = True

            except (Psycopg2Error, OperationalError):
                self.stdout.write("Database not available, waiting 1 second...")
                time.sleep(1)

        self.stdout.write("PostgresSQL Database is available")
