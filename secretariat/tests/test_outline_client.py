from unittest import mock

from django.test import TestCase

import secretariat.tests.outline_mocks as mocks
from secretariat.utils.outline import Client, GroupCreationFailed, RemoteServerError


class TestOutlineClient(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tested = Client()

    @mock.patch("requests.post")
    def test_list_users_when_all_is_fine(self, mock_post):
        client = Client()
        mock_post.return_value = mocks.list_response_ok()

        response = client.list_users("")
        self.assertTrue(mock_post.called, "The client should send a POST request")
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

        self.assertTrue(mock_post.called, "The client should send a POST request")

    @mock.patch("requests.post")
    def test_create_group_when_all_is_fine(self, mock_post):
        client = Client()
        mock_post.return_value = mocks.group_creation_ok()
        uuid = client.create_new_group("Oh le joli groupe")
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
        self.assertTrue(mock_post.called, "The client should send a POST request")
