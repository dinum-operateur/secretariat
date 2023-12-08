from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError
from factory import Faker

from config.settings import OUTLINE_URL
from secretariat.models import Membership, Organisation
from secretariat.utils.outline import Client as OutlineClient
from secretariat.utils.outline import RemoteServerError

User = get_user_model()


class Command(BaseCommand):
    help = "Imports users from Outline. Creates missing users in Django, updates existing users if needed."

    def handle(self, *args, **options):
        print(f"Instance URL is {OUTLINE_URL} .")

        client = OutlineClient()

        self.import_users(client)
        self.import_orga_and_memberships(client)

    def import_users(self, client):
        self.stdout.write("Importing users ... ")

        # we list known mails to try and match users
        known_emails = set(value[0] for value in User.objects.values_list("email"))
        count_existing_users, count_new_users, count_errors = 0, 0, 0

        for user in self.get_all_outline_users(client):
            if user["email"] in known_emails:
                django_user = User.objects.get(email=user["email"])
                if str(django_user.outline_uuid) == user["id"]:
                    count_existing_users += 1
                elif django_user.outline_uuid is None:
                    django_user.outline_uuid = user["id"]
                    django_user.save()
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Unexpected UUID for {django_user.username} (django: '{django_user.outline_uuid}', outline: '{user['id']}')."
                        )
                    )
                    count_errors += 1
            else:
                try:
                    self.create_new_django_user(user)
                except IntegrityError:
                    count_errors += 1
                except ValidationError:
                    count_errors += 1
                else:
                    count_new_users += 1

        self.stdout.write(
            f"\n{count_existing_users} utilisateurices déjà à jour sur secretariat."
        )
        self.stdout.write(f"{count_new_users} nouveaux users.")
        self.stdout.write(self.style.ERROR(f"{count_errors} erreurs.\n"))

    def get_all_outline_users(self, client):
        try:
            offset = 0
            limit = 25
            users_page = None
            while users_page != []:
                users_page = client.list_users(offset=offset, limit=limit)
                yield from users_page
                offset += limit

        except RemoteServerError:
            self.stdout.write(self.style.ERROR("Cannot reach remote server."))
            exit()

    def create_new_django_user(self, outline_user):
        django_user = User(
            username=outline_user["name"].replace(" ", "").lower(),
            first_name=outline_user["name"].split(" ")[0],
            last_name=" ".join(outline_user["name"].split(" ")[1:]),
            email=outline_user["email"],
            outline_uuid=outline_user["id"],
            password=Faker("password"),
        )
        try:
            django_user.full_clean()
            django_user.save()
        except IntegrityError:
            self.stdout.write(
                self.style.ERROR(
                    f"Impossible d'ajouter '{django_user.username}' car cet username existe déjà dans Django. Veuillez choisir un username différent ou supprimer le doublon avant de réessayer."
                )
            )

    def get_all_outline_groups(self, client):
        try:
            offset = 0
            limit = 25
            groups_page = None
            while groups_page != []:
                groups_page = client.list_groups(offset=offset, limit=limit)
                yield from groups_page
                offset += limit

        except RemoteServerError:
            self.stdout.write(self.style.ERROR("Impossible d'atteindre le serveur."))
            exit()

    def import_orga_and_memberships(self, client):
        self.stdout.write("Import des groupes ...")
        known_group_names = set(
            value[0] for value in Organisation.objects.values_list("name")
        )
        known_group_uuids = set(
            str(value[0])
            for value in Organisation.objects.values_list("outline_group_uuid")
        )
        count_existing_orgas, count_new_groups, count_errors = 0, 0, 0

        for outline_group in self.get_all_outline_groups(client):
            if str(outline_group["id"]) in known_group_uuids:
                count_existing_orgas += 1
                django_orga = Organisation.objects.get(
                    outline_group_uuid=outline_group["id"]
                )
                prompt_already_existing = f'L\'organisation "{outline_group["name"]}" existe déjà sur secretariat.'

                if django_orga.name != outline_group["name"]:
                    django_orga.name = outline_group["name"]
                    django_orga.save()

            elif outline_group["name"] in known_group_names:
                count_existing_orgas += 1
                django_orga = Organisation.objects.get(name=outline_group["name"])

                prompt_already_existing = f'L’orga "{outline_group["name"]}" existe déjà dans l’app secrétariat'
                if str(django_orga.outline_group_uuid) != outline_group["id"]:
                    if django_orga.outline_group_uuid is None:
                        self.stdout.write(
                            self.style.WARNING(
                                f"{prompt_already_existing}, sans UUID précisé. UUID copié depuis Outline."
                            )
                        )
                        django_orga.outline_group_uuid = outline_group["id"]
                        django_orga.save()
                    else:
                        self.stdout.write(
                            self.style.ERROR(
                                f"{prompt_already_existing}. Les UUID ne correspondent pas (django: '{django_orga.outline_group_uuid}', outline: '{outline_group['id']}')."
                            )
                        )
                        count_errors += 1
            else:
                try:
                    django_orga = self.create_new_django_orga(outline_group)
                    count_new_groups += 1
                except IntegrityError:
                    count_errors += 1

            # then lists group members on django and outline

            # we then prepare a set listing every member of the group in Django. We'll remove outline members.
            # The remaining list should be empty. If not, users might have been removed directly in outline of here
            # django users were not properly synced to outline
            django_users_unaccounted_for = set(
                value[0] for value in django_orga.members.values_list("username")
            )

            # and get or create memberships for all users found in outline group
            count_added_members = 0
            for member in client.list_group_users(outline_group["id"]):
                django_user = User.objects.get(outline_uuid=member["id"])

                try:
                    membership, is_created = Membership.objects.get_or_create(
                        user=django_user,
                        organisation=django_orga,
                        role="admin" if member["isAdmin"] else "member",
                    )
                    if is_created:
                        membership.save()
                        count_added_members += 1
                    else:
                        django_users_unaccounted_for.remove(django_user.username)
                except Exception as exception:
                    print("Exception : ", exception)

            if count_added_members != 0:
                print(
                    f"{count_added_members} membres ajouté.es au groupe {django_orga.name}."
                )

        # Every member should be accounted for. Warn user otherwise
        print(
            len(django_users_unaccounted_for), "souci(s) de permissions après import."
        )
        if len(django_users_unaccounted_for) != 0:
            print("Veuillez vérifier/synchroniser les groupes des membres suivants :")
            for extra_django_member in django_users_unaccounted_for:
                print("   - ", extra_django_member)

        self.stdout.write(
            f"\n{count_existing_orgas} organisations déjà à jour sur secretariat."
        )
        self.stdout.write(f"{count_new_groups} organisations créées.")
        self.stdout.write(self.style.ERROR(f"{count_errors} erreurs."))

    def create_new_django_orga(self, outline_group):
        django_orga = Organisation(
            name=outline_group["name"],
            outline_group_uuid=outline_group["id"],
        )
        try:
            django_orga.full_clean()
            django_orga.save()
        except IntegrityError:
            self.stdout.write(
                self.style.ERROR(
                    f"Impossible d'ajouter '{outline_group.name}' car ce groupe existe déjà dans Django. Veuillez choisir un nom de groupe différent ou supprimer le doublon avant de réessayer."
                )
            )
        else:
            self.stdout.write(f"Création du groupe {django_orga.name}.")

        return django_orga
