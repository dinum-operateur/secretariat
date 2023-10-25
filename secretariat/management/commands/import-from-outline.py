from django.core.management.base import BaseCommand

from config.settings import OUTLINE_API_URL
from secretariat.utils.outline import Client as OutlineClient


class Command(BaseCommand):
    help = "Imports users from Outline. Creates missing users in Django, updates existing users if needed."

    def handle(self, *args, **options):
        client = OutlineClient()

        self.stdout.write(f"Importing users from instance {OUTLINE_API_URL}.")

        outline_users = client.list_users()
        for user in outline_users:
            self.stdout.write(self.style.SUCCESS(user["name"]))
