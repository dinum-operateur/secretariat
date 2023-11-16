from unittest import mock, skipUnless

from django.test import TestCase

import secretariat.tests.outline_mocks as mocks
from config.settings import OUTLINE_API_TOKEN, OUTLINE_OPI_GROUP_ID, OUTLINE_URL
from secretariat.tests.factories import UserFactory
from secretariat.utils.outline import (
    Client,
    GroupCreationFailed,
    InvalidRequest,
    InvitationFailed,
    RemoteServerError,
)


class TestOutlineClient(TestCase):
    @mock.patch("requests.post")
    def test_list_users_when_all_is_fine(self, mock_post):
        client = Client()
        mock_post.return_value = mocks.list_response_ok()

        response = client.list_users("")
        self.assertTrue(
            mock_post.called, "A POST request should have been sent at some point"
        )
        self.assertEqual(len(response), 1, "Response should contain a list of 1 user")
        first_user = response[0]
        self.assertEqual(
            first_user["name"],
            "Prudence Crandall",
            "First user should be Prudence Crandall",
        )

    @mock.patch("requests.post")
    def test_list_users_when_unauthorized(self, mock_post):
        client = Client()
        mock_post.return_value.status_code = 401

        with self.assertRaises(RemoteServerError) as cm:
            client.list_users("the query")

        exception = cm.exception
        self.assertEqual(exception.status_code, 401)

        self.assertTrue(
            mock_post.called, "A POST request should have been sent at some point"
        )

    @mock.patch("requests.post")
    def test_invite_user_when_all_is_fine(self, mock_post):
        client = Client()
        mock_post.return_value = mocks.invite_response_ok()

        response = client.invite_to_outline(UserFactory())
        self.assertTrue(
            mock_post.called, "A POST request should have been sent at some point"
        )
        self.assertEqual(
            "26985a73-9fc5-4c31-839c-51304daf2628",
            response,
            "Response should be the UUID of the new user",
        )

    @mock.patch("requests.post")
    def test_invite_already_invited_user(self, mock_post):
        client = Client()
        mock_post.return_value = mocks.invite_response_already_invited()
        with self.assertRaises(InvitationFailed):
            client.invite_to_outline(UserFactory())
        self.assertTrue(
            mock_post.called, "A POST request should have been sent at some point"
        )

    @mock.patch("requests.post")
    def test_invite_user_invalid_email(self, mock_post):
        client = Client()
        mock_post.return_value = mocks.invite_response_invalid_email()

        with self.assertRaises(InvalidRequest) as cm:
            client.invite_to_outline(UserFactory(email="agnès.ql@test.gouv.fr"))

        exception = cm.exception
        self.assertEqual(exception.status_code, 400)
        self.assertIn("Invalid email", exception.error_message)

        self.assertTrue(
            mock_post.called, "A POST request should have been sent at some point"
        )

    @mock.patch("requests.post")
    def test_invite_when_outline_is_out(self, mock_post):
        client = Client()
        mock_post.return_value.status_code = 502

        with self.assertRaises(RemoteServerError) as cm:
            client.invite_to_outline(UserFactory())

        exception = cm.exception
        self.assertEqual(exception.status_code, 502)

        self.assertTrue(
            mock_post.called, "A POST request should have been sent at some point"
        )

    @mock.patch("requests.post")
    def test_create_group_when_all_is_fine(self, mock_post):
        client = Client()
        mock_post.return_value = mocks.group_creation_ok()
        uuid = client.create_new_group("Ce groupe va se créer facilement")
        self.assertEqual(
            uuid,
            "29907d66-d23f-46e9-be9b-92e2820b81aa",
            "Group should be created on outline and uuid returned",
        )

    @mock.patch("requests.post")
    def test_create_group_but_it_exists(self, mock_post):
        client = Client()
        mock_post.return_value = mocks.group_creation_ko_already_exists()
        with self.assertRaises(GroupCreationFailed) as cm:
            client.create_new_group("Oh le joli groupe ENCORE")
        exception = cm.exception
        self.assertEqual(exception.status_code, 400)
        self.assertTrue(
            mock_post.called, "A POST request should have been sent at some point"
        )

    @skipUnless(
        OUTLINE_API_TOKEN and OUTLINE_URL and OUTLINE_OPI_GROUP_ID,
        "Skip test in case of missing outline configuration",
    )
    def test_find_group_by_name(self):
        client = Client()
        my_group_name = "Oh le joli groupe"
        group = client.find_group_by_name(my_group_name)
        self.assertEqual("9a33fcb1", group.get("id")[:8])
        self.assertEqual(my_group_name, group.get("name"))
