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
        user = User(
            first_name="prudence",
            last_name="crandall",
            username="pcrandall",
            email="prudence.crandall@gouv.fr",
            password="whatever",
        )

        response = self.list_outline_users(query=f"{user.first_name} {user.last_name}")
        self.assertEqual(response.json()["pagination"]["total"], 0)

        user.save()
        self.assertTrue(user in User.objects.all())

        response = self.list_outline_users(query=f"{user.first_name} {user.last_name}")
        self.assertEqual(response.json()["pagination"]["total"], 1)
        self.assertEqual(response.json()["data"][0]["email"], user.email)
