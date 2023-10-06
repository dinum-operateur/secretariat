import requests
from django.contrib.auth.models import AbstractUser
from django.db import models

from config.settings import OUTLINE_API_TOKEN, OUTLINE_API_URL


class User(AbstractUser):
    outline_uuid = models.CharField(max_length=25, blank=False, null=False)

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        self.invite_to_outline()
        self.add_to_outline_groups(user_uuid=self.outline_uuid, group="OPI")

    def invite_to_outline(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {OUTLINE_API_TOKEN}",
        }
        response = requests.post(
            url=f"{OUTLINE_API_URL}/users.invite",
            headers=headers,
            json={
                "invites": [
                    {
                        "name": f"{self.first_name} {self.last_name}",
                        "email": self.email,
                        "role": "member",
                    }
                ]
            },
        )
        self.outline_uuid = response.json()["data"]["users"][0]["id"]

    def add_to_outline_groups(self, user_uuid, group):
        pass
