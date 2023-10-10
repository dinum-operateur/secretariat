from unittest import mock

from django.test import TestCase

import secretariat.tests.outline_mocks as mocks
from secretariat.utils.outline import Client, RemoteServerError


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
