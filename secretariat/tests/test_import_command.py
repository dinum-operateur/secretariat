from django.core.management import call_command
from django.test import TestCase

from secretariat.models import Membership, Organisation, User
from secretariat.tests.factories import (
    MembershipFactory,
    OrganisationFactory,
    UserFactory,
)
from secretariat.utils.outline import Client as OutlineClient


class TestSynchronizationCommand(TestCase):
    outline_client = OutlineClient()

    def test_synchronizing_new_user_from_outline_adds_them_to_django(self):
        outline_user = UserFactory.build()
        outline_user.outline_uuid = self.outline_client.invite_to_outline(outline_user)

        self.assertFalse(
            User.objects.filter(email=outline_user.email).exists(),
            "User should not exist on Django (yet)",
        )
        call_command("import-from-outline")

        self.assertTrue(
            User.objects.filter(email=outline_user.email).exists(),
            "User should now exist.",
        )

        self.outline_client.remove_user_from_outline(outline_user)

    def test_importing_from_outline_imports_new_empty_orga(self):
        outline_group = OrganisationFactory.build()
        outline_group.outline_group_uuid = self.outline_client.create_new_group(
            outline_group.name
        )

        self.assertFalse(
            Organisation.objects.filter(name=outline_group.name).exists(),
            "Orga should not exist on Django (yet)",
        )
        call_command("import-from-outline")

        self.assertTrue(
            Organisation.objects.filter(name=outline_group.name).exists(),
            "Organization should now exist.",
        )

        self.outline_client.delete_group_from_outline(outline_group)

    def test_importing_from_outline_imports_new_orga_and_memberships(self):
        outline_membership = MembershipFactory.build()
        self.outline_client.add_to_outline_group(
            outline_membership.user, outline_membership.organisation
        )

        self.assertFalse(
            Membership.objects.filter(
                user=outline_membership.user,
                organisation=outline_membership.organisation,
            ).exists(),
            "Membership should not exist on Django (yet)",
        )

        call_command("import-from-outline")
        self.assertTrue(
            Membership.objects.filter(
                user=outline_membership.user,
                organisation=outline_membership.organisation,
            ).exists(),
            "Membership should now exist",
        )

        self.outline_client.remove_user_from_outline(
            outline_membership.user,
        )
        self.outline_client.delete_group_from_outline(outline_membership.organisation)
