import requests
from django.test import TestCase

from config.settings import OUTLINE_API_TOKEN, OUTLINE_API_URL, OUTLINE_OPI_GROUP_ID
from secretariat.models import User
from secretariat.tests.factories import UserFactory

DEFAULT_OUTLINE_UUID = "not a valid uuid"


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

    def test_creating_user_adds_them_to_outline(self):
        user = UserFactory()
        query = f"{user.first_name} {user.last_name}"
        response = self.list_outline_users(query=query)
        self.assertEqual(
            response.json()["pagination"]["total"],
            0,
            f"Found an existing outline user with query {query}",
        )

        user.save()
        self.assertTrue(user in User.objects.all())

        response = self.list_outline_users(query=f"{user.first_name} {user.last_name}")
        self.assertNotEqual(
            user.outline_uuid,
            DEFAULT_OUTLINE_UUID,
            "Outline UUID should be correctly filled on user after save",
        )
        self.assertEqual(
            response.json()["pagination"]["total"],
            1,
            "User should be invited on outline after save",
        )
        self.assertEqual(
            response.json()["data"][0]["email"],
            user.email,
            "User should have same email in django and outline",
        )

        self.removeUserFromOutline(user)

    def test_creating_user_adds_them_to_opi_group_in_outline(self):
        user = UserFactory()
        query = f"{user.first_name} {user.last_name}"
        memberships_before_save = requests.post(
            url=f"{OUTLINE_API_URL}/groups.memberships",
            headers=self.headers,
            json={"id": OUTLINE_OPI_GROUP_ID, "offset": 0, "limit": 25, "query": query},
        )

        self.assertFalse(
            any(
                outline_user["name"] == query
                for outline_user in memberships_before_save.json()["data"]["users"]
            ),
            "New user should not be in any outline group before first save",
        )
        member_count_before_save = len(memberships_before_save.json()["data"]["users"])

        user.save()
        self.assertTrue(user in User.objects.all())

        memberships_after_save = requests.post(
            url=f"{OUTLINE_API_URL}/groups.memberships",
            headers=self.headers,
            json={
                "id": OUTLINE_OPI_GROUP_ID,
                "offset": 0,
                "limit": 25,
                "query": query,
            },
        )
        self.assertEqual(
            len(memberships_after_save.json()["data"]["users"]),
            member_count_before_save + 1,
            "OPI group should contain one more member after user save.",
        )
        self.assertTrue(
            any(
                outline_user["name"] == query
                for outline_user in memberships_after_save.json()["data"]["users"]
            ),
            "New user should be in the outline group after save",
        )
        self.assertNotEqual(
            user.outline_uuid,
            DEFAULT_OUTLINE_UUID,
            "Outline UUID should be filled in django user after save",
        )
        self.removeUserFromOutline(user)

    def removeUserFromOutline(self, user: User):
        requests.post(
            url=f"{OUTLINE_API_URL}/users.delete",
            headers=self.headers,
            json={
                "id": user.outline_uuid,
            },
        )
