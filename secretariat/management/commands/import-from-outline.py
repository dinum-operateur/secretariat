from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from config.settings import OUTLINE_URL
from secretariat.utils.outline import Client as OutlineClient
from secretariat.utils.outline import RemoteServerError

User = get_user_model()


class Command(BaseCommand):
    help = "Imports users from Outline. Creates missing users in Django, updates existing users if needed."

    def add_arguments(self, parser):
        parser.add_argument(
            "--users-only", action="store_true", help="import users only"
        )
        parser.add_argument(
            "--groups-only", action="store_true", help="import groups only"
        )

    def handle(self, *args, **options):
        if options["users_only"] and options["groups_only"]:
            raise CommandError(
                "options --users-only and --groups-only cannot be used at the same time. For both users and groups, use neither."
            )

        print(f"Instance URL is {OUTLINE_URL} .")
        # check instance is up ?

        client = OutlineClient()

        importing_users = True if not options["groups_only"] else False
        importing_groups = True if not options["users_only"] else False

        if importing_users:
            self.stdout.write("Importing users ... ")

            try:
                offset = 0
                limit = 25
                outline_users = []
                users_page = None
                while users_page != []:
                    users_page = client.list_users(offset=offset, limit=limit)
                    outline_users += users_page
                    offset += 25

            except RemoteServerError:
                self.stdout.write(self.style.ERROR("Cannot reach remote server."))
                exit()

            known_emails = set(value[0] for value in User.objects.values_list("email"))
            count_existing_users, count_new_users, count_errors = 0, 0, 0

            for user in outline_users:
                if user["email"] in known_emails:
                    django_user = User.objects.get(email=user["email"])

                    prompt_already_existing = (
                        f'Email {user["email"]} already on secretariat app'
                    )
                    if str(django_user.outline_uuid) == user["id"]:
                        count_existing_users += 1
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
                        count_errors += 1
                else:
                    try:
                        self.create_new_django_user(user)
                    except IntegrityError:
                        count_errors += 1

            self.stdout.write(f"\nMatched {count_existing_users} existing users.")
            self.stdout.write(f"Created {count_new_users} new Django users.")
            self.stdout.write(self.style.ERROR(f"{count_errors} errors."))

        if importing_groups:
            self.stdout.write("Importing groups ...")

            try:
                offset = 0
                limit = 25
                outline_groups = []
                groups_page = None
                while groups_page != []:
                    groups_page = client.list_groups(offset=offset, limit=limit)
                    outline_groups += groups_page
                    offset += 25

            except RemoteServerError:
                self.stdout.write(self.style.ERROR("Cannot reach remote server."))
                exit()

            print(f"Found {len(outline_groups)} groups.")
            # WIP

    def create_new_django_user(self, outline_user):
        django_user = User(
            username=outline_user["name"].replace(" ", "").lower(),
            first_name=outline_user["name"].split(" ")[0],
            last_name=" ".join(outline_user["name"].split(" ")[1:]),
            email=outline_user["email"],
            outline_uuid=outline_user["id"],
        )
        try:
            django_user.save()
        except IntegrityError as error:
            self.stdout.write(
                self.style.ERROR(
                    f"Impossible d'ajouter '{django_user.username}' car cet username existe déjà dans Django. Veuillez choisir un username différent ou supprimer le doublon avant de réessayer."
                )
            )
            raise error

        self.stdout.write(f'Creating user {outline_user["name"]}')
