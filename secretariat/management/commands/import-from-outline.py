from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from config.settings import OUTLINE_API_URL
from secretariat.utils.outline import Client as OutlineClient
from secretariat.utils.outline import RemoteServerError

User = get_user_model()


class Command(BaseCommand):
    help = "Imports users from Outline. Creates missing users in Django, updates existing users if needed."

    def handle(self, *args, **options):
        client = OutlineClient()

        self.stdout.write(f"Importing users from instance {OUTLINE_API_URL}.")

        try:
            outline_users = client.list_users()
        except RemoteServerError:
            self.stdout.write(
                self.style.ERROR("Couldn't not reach remote server. Exiting.")
            )

        known_emails = [value[0] for value in User.objects.values_list("email")]
        count_existing_users, count_new_users, count_mismatched = 0, 0, 0

        for user in outline_users:
            if user["email"] in known_emails:
                count_existing_users += 1
                django_user = User.objects.get(email=user["email"])

                prompt_already_existing = (
                    f'Email {user["email"]} already on secretariat app'
                )
                if django_user.outline_uuid == user["id"]:
                    self.stdout.write(f"{prompt_already_existing}.")
                elif django_user.outline_uuid is None:
                    self.stdout.write(
                        self.style.WARNING(
                            f"{prompt_already_existing}, with no UUID. Copying UUID from outline."
                        )
                    )
                    django_user.outline_uuid = user["id"]
                    django_user.save()
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"{prompt_already_existing}. Unexpected UUID (django: '{django_user.outline_uuid}', outline: '{user['id']}')."
                        )
                    )
                    count_mismatched += 1
            else:
                new_user = User(
                    username=user["name"].replace(" ", "").lower(),
                    first_name=user["name"].split(" ")[0],
                    last_name=" ".join(user["name"].split(" ")[1:]),
                    email=user["email"],
                    outline_uuid=user["id"],
                )
                new_user.save()
                count_new_users += 1
                self.stdout.write(f'Creating user {user["name"]}')

        self.stdout.write(f"\nMatched {count_existing_users} existing users.")
        self.stdout.write(f"Created {count_new_users} new django users.")
        self.stdout.write(self.style.ERROR(f"{count_mismatched} mismatched."))
