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
        # vérifier que post a été appelé requests.post
        self.assertTrue(mock_post.called, "Aucune requête POST n'a été faite")
        self.assertEqual(len(response), 1, "On n'a pas de user dans la réponse")
        first_user = response[0]
        self.assertEqual(first_user["name"], "Jane Doe")

    @mock.patch("requests.post")
    def test_list_users_when_unauthorized(self, mock_post):
        client = Client()
        mock_post.return_value.status_code = 401

        with self.assertRaises(RemoteServerError) as cm:
            client.list_users("the query")

        exception = cm.exception
        self.assertEqual(exception.status_code, 401)

        self.assertTrue(mock_post.called, "Aucune requête POST n'a été faite")

    def test_list_users_when_server_not_found(self):
        pass
