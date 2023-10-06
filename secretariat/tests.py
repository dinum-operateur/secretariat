import requests
from django.test import TestCase

from config.settings import OUTLINE_API_TOKEN, OUTLINE_API_URL
from secretariat.models import User


class TestUser(TestCase):
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {OUTLINE_API_TOKEN}",
    }
    test_user = User(
        first_name="prudence",
        last_name="crandall",
        username="pcrandall",
        email="prudence.crandall@gouv.fr",
        password="whatever",
    )

    def list_outline_users(self, query):
        response = requests.post(
            url=f"{OUTLINE_API_URL}/users.list",
            headers=self.headers,
            json={
                "offset": 0,
                "limit": 25,
                "sort": "updatedAt",
                "direction": "DESC",
                "query": query,
                "filter": "all",
            },
        )
        return response

    def test_creating_user_here_adds_them_to_outline(self):
        user = self.test_user

        response = self.list_outline_users(query=f"{user.first_name} {user.last_name}")
        self.assertEqual(response.json()["pagination"]["total"], 0)

        user.save()
        self.assertTrue(user in User.objects.all())

        response = self.list_outline_users(query=f"{user.first_name} {user.last_name}")
        self.assertEqual(response.json()["pagination"]["total"], 1)
        self.assertEqual(response.json()["data"][0]["email"], user.email)

    # def test_creating_user_saves_outline_uuid(self):
    #     pass

    def tearDown(self):
        # tearDown method to remove invited test_user from Outline staging
        # will become obsolete when mocking outline client
        test_user = User.objects.get(username=self.test_user.username)

        requests.post(
            url=f"{OUTLINE_API_URL}/users.delete",
            headers=self.headers,
            json={
                "id": test_user.outline_uuid,
            },
        )
