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

    def test_creating_user_here_adds_them_to_outline(self):
        print(OUTLINE_API_URL)
        response = requests.post(
            url=f"{OUTLINE_API_URL}/users.list",
            headers=self.headers,
            json={
                "offset": 0,
                "limit": 25,
                "sort": "updatedAt",
                "direction": "DESC",
                "query": "pcrandall",
                "filter": "all",
            },
        )
        print(response)
        self.assertEqual(response.json()["pagination"]["total"], 0)

        user = User(
            username="pcrandall", email="prudence.crandall@gouv.fr", password="whatever"
        )
        user.save()
        self.assertTrue(user in User.objects.all())

        response = requests.post(
            url=f"{OUTLINE_API_URL}/users.list",
            headers=self.headers,
            json={
                "offset": 0,
                "limit": 25,
                "sort": "updatedAt",
                "direction": "DESC",
                "query": "pcrandall",
                "filter": "all",
            },
        )
        self.assertTrue(response.json()["pagination"]["total"], 1)
