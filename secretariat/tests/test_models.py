from datetime import date, timedelta
from unittest.mock import patch

from django.db.utils import IntegrityError
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

    def test_synchro_with_outline(self):
        test_uuid = "99cb30d7-833d-4d0a-ba70-a0403fc72554"
        with patch("secretariat.utils.outline.Client") as MockedOutlineClient:
            mocked_client_instance = MockedOutlineClient.return_value
            mocked_client_instance.create_new_group.return_value = test_uuid

            organisation = OrganisationFactory()
            self.assertIsNone(
                organisation.outline_group_uuid,
                "organisation.outline_group_uuid should be None before first sync",
            )

            organisation.synchronize_to_outline()
            self.assertEqual(
                organisation.outline_group_uuid,
                test_uuid,
                "organisation.outline_group_uuid should be the one returned by Outline after first sync",
            )

    def test_membership_cannot_end_before_beginning(self):
        wrong_end_date = date.today() - timedelta(days=100)
        with self.assertRaises(IntegrityError):
            membership = MembershipFactory(
                start_date=date.today(), end_date=wrong_end_date
            )
            membership.full_clean()
            membership.save()

    def test_membership_cannot_end_same_day_as_beginning(self):
        with self.assertRaises(IntegrityError):
            membership = MembershipFactory(
                start_date=date.today(), end_date=date.today()
            )
            membership.full_clean()
            membership.save()

    def test_membership_start_date_can_be_null(self):
        membership = MembershipFactory(end_date=date.today())
        self.assertTrue(membership.start_date is None)

        membership.full_clean()
        membership.save()
        self.assertTrue(membership.end_date == date.today())
        self.assertTrue(membership.start_date is None)

    def test_membership_end_date_can_be_null(self):
        membership = MembershipFactory(start_date=date.today())
        self.assertTrue(membership.end_date is None)

        membership.full_clean()
        membership.save()
        self.assertTrue(membership.start_date == date.today())
        self.assertTrue(membership.end_date is None)

    def test_membership_dates_can_be_null(self):
        membership = MembershipFactory()
        self.assertTrue(membership.start_date is None)
        self.assertTrue(membership.end_date is None)

        membership.full_clean()
        membership.save()
        self.assertTrue(membership.start_date is None)
        self.assertTrue(membership.end_date is None)
