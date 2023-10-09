import requests

from config.settings import OUTLINE_API_TOKEN, OUTLINE_API_URL
from secretariat.models import User

# from django.auth.contrib import get_user_model

# User = get_user_model()


class Client:
    url = OUTLINE_API_URL
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {OUTLINE_API_TOKEN}",
    }

    def invite_to_outline(self, user: User):
        response = requests.post(
            url=f"{self.url}/users.invite",
            headers=self.headers,
            json={
                "invites": [
                    {
                        "name": f"{user.first_name} {user.last_name}",
                        "email": user.email,
                        "role": "member",
                    }
                ]
            },
        )
        user_uuid = response.json()["data"]["users"][0]["id"]
        return user_uuid

    def add_to_outline_group(self, user_uuid, group):
        requests.post(
            url=f"{self.url}/groups.add_user",
            headers=self.headers,
            json={
                "id": group,
                "userId": user_uuid,
            },
        )
