from django.test import TestCase

from secretariat.models import Organisation, User
from secretariat.tests.factories import (
    MembershipFactory,
    OrganisationFactory,
    UserFactory,
)


class TestMembership(TestCase):
    def test_user_organisations(self):
        user = UserFactory()
        for _ in range(5):
            MembershipFactory(user=user)
        self.assertEqual(len(user.organisations), 5, "User should have 5 organisations")
        for org in user.organisations:
            self.assertIsInstance(
                org,
                Organisation,
                "objects of user.organisations should be Organisations",
            )

    def test_organisation_members(self):
        organisation = OrganisationFactory()
        for _ in range(5):
            MembershipFactory(organisation=organisation)
        self.assertEqual(
            len(organisation.members), 5, "Organisation should have 5 members"
        )
        for user in organisation.members:
            self.assertIsInstance(
                user, User, "objects of organisation.members should be Users"
            )
