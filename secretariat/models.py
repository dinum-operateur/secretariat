import requests
from django.contrib.auth.models import AbstractUser

from config.settings import OUTLINE_API_TOKEN, OUTLINE_API_URL


class User(AbstractUser):
    pass

    def save(self, *args, **kwargs):
        super(User, self).save(*args, **kwargs)
        self.invite_to_outline()

    def invite_to_outline(self):
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {OUTLINE_API_TOKEN}",
        }
        requests.post(
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
