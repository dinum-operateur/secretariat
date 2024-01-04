from unittest import skipUnless

from django.test import TestCase

from config.settings import OUTLINE_API_TOKEN, OUTLINE_URL
from secretariat.models import User
from secretariat.tests.factories import (
    MembershipFactory,
    OrganisationFactory,
    UserFactory,
)
from secretariat.utils.outline import Client as OutlineClient


@skipUnless(
    OUTLINE_API_TOKEN and OUTLINE_URL,
    "Skip test in case of missing outline configuration",
)
class TestUserSynchronization(TestCase):
    outline_client = OutlineClient()

    def test_add_user_to_outline(self):
        user = UserFactory()
        query = f"{user.first_name} {user.last_name}"
        response = self.outline_client.list_users(query)
        self.assertEqual(
            len(response),
            0,
            f"No user should exist in outline with query '{query}', before first sync",
        )

        self.assertTrue(user in User.objects.all())

        user.synchronize_to_outline()

        self.assertIsNotNone(
            user.outline_uuid,
            "Outline UUID should be correctly filled on user after save",
        )
        response = self.outline_client.list_users(query)
        self.assertEqual(
            len(response),
            1,
            f"One user should exist in outline with query '{query}', after sync",
        )
        self.assertEqual(
            response[0]["email"],
            user.email,
            "User should have the same email in django and outline",
        )

        self.outline_client.remove_user_from_outline(user)

    def test_invite_existing_user_gets_their_uuid(self):
        thibaut = UserFactory(email="thibaut.denis@fictif.pour.test.gouv.fr")
        query = "Thibaut Denis"
        response = self.outline_client.list_users(query)
        self.assertEqual(
            len(response),
            1,
            "Thibaut Denis should already exist in Outline Staging",
        )

        self.assertTrue(thibaut in User.objects.all())

        thibaut.synchronize_to_outline()

        self.assertIsNotNone(
            thibaut.outline_uuid,
            "Outline UUID should be correctly filled on user after save",
        )
        self.assertEqual(
            "0640461e",
            thibaut.outline_uuid[:8],
        )
        response = self.outline_client.list_users(query)
        self.assertEqual(
            len(response),
            1,
            f"One user should exist in outline with query '{query}', after sync",
        )
        self.assertEqual(
            response[0]["email"],
            thibaut.email,
            "User should have the same email in django and outline",
        )

    def test_removing_user_from_organisation_should_removes_them_from_outline_group(
        self,
    ):
        user = UserFactory()
        user.outline_uuid = self.outline_client.invite_to_outline(user)
        orga = OrganisationFactory()
        orga.outline_group_uuid = self.outline_client.create_new_group(orga.name)
        membership = MembershipFactory(user=user, organisation=orga)
        self.outline_client.add_to_outline_group(
            user.outline_uuid, orga.outline_group_uuid
        )

        outline_memberships = self.outline_client.list_user_memberships(user)
        self.assertTrue(
            next(
                (
                    True
                    for elem in outline_memberships
                    if orga.outline_group_uuid in elem["groupId"]
                ),
                False,
            ),
            "User should be listed in newly created group.",
        )

        membership.delete()
        user.synchronize_to_outline()

        outline_memberships = self.outline_client.list_user_memberships(user)
        self.assertFalse(
            next(
                (
                    True
                    for elem in outline_memberships
                    if orga.outline_group_uuid in elem["groupId"]
                ),
                False,
            ),
            "User should not be listed in any group.",
        )

        self.outline_client.remove_user_from_outline(user)
        self.outline_client.delete_group_from_outline(orga)
