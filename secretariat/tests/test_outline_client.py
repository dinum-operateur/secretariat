from unittest import mock

from django.test import TestCase
from requests import Response

from secretariat.utils.outline import Client, RemoteServerError


class TestOutlineClient(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.tested = Client()

    @mock.patch("requests.post")
    def test_list_users_when_all_is_fine(self, mock_post):
        client = Client()
        mock_response = mock_post.return_value
        mock_response = Response()
        mock_response.status_code = 200
        mock_response.encoding = "utf-8"
        mock_response.content = """
        {
          "data": [
            {
              "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
              "name": "Jane Doe",
              "avatarUrl": "http://example.com",
              "email": "jane@example.com",
              "isAdmin": true,
              "isSuspended": true,
              "lastActiveAt": "2019-08-24T14:15:22Z",
              "createdAt": "2019-08-24T14:15:22Z"
            }
          ],
          "pagination": {
            "offset": 0,
            "limit": 25
          }
        }
        """

        response = client.list_users("")
        # vérifier que post a été appelé requests.post
        self.assertTrue(mock_post.called, "Aucune requête POST n'a été faite")
        self.assertEqual(len(response), 1, "On n'a pas de user dans la réponse")
        first_user = response[0]
        self.assertEqual(first_user.name, "Jane Doe")

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
