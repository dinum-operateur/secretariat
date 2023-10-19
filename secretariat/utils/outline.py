import requests

from config.settings import OUTLINE_API_TOKEN, OUTLINE_API_URL
from secretariat.models import User


class OutlineAPIClientError(Exception):
    pass


class RemoteServerError(OutlineAPIClientError):
    def __init__(self, error_code):
        self.status_code = error_code


class InvitationFailed(OutlineAPIClientError):
    def __init__(self, error_code):
        self.status_code = error_code


class EmailInvitedMoreThanOnce(OutlineAPIClientError):
    def __init__(self, error_code):
        self.status_code = error_code


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
        if len(response.json()["data"]["users"]) == 0:
            raise InvitationFailed(response.status_code)

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

    def retrieve_user_by_email(self, email):
        response = requests.post(
            url=f"{self.url}/users.list",
            headers=self.headers,
            json={
                "offset": 0,
                "limit": 25,
                "sort": "updatedAt",
                "direction": "DESC",
                "emails[]": email,
                "filter": "all",
            },
        )
        if len(response.json()["data"]) != 1:
            raise EmailInvitedMoreThanOnce(response.status_code)

        return response.json()["data"]

    def list_users(self, query):
        response = requests.post(
            url=f"{self.url}/users.list",
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
        if response.status_code != 200:
            raise RemoteServerError(response.status_code)

        return response.json()["data"]
