import requests

from config.settings import OUTLINE_API_TOKEN, OUTLINE_API_URL
from secretariat.models import User


class OutlineAPIClientError(Exception):
    def __init__(self, error_code, error_message=""):
        self.status_code = error_code
        self.error_message = error_message


class RemoteServerError(OutlineAPIClientError):
    pass


class InvitationFailed(OutlineAPIClientError):
    pass


class GroupCreationFailed(OutlineAPIClientError):
    pass


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

    def create_new_group(self, group_name):
        response = requests.post(
            url=f"{self.url}/groups.create",
            headers=self.headers,
            json={"name": group_name},
        )
        if response.status_code >= 500:
            raise RemoteServerError(response.status_code)

        if response.status_code == 400:
            object = response.json()
            raise GroupCreationFailed(
                400, f"{object.get('error')} - {object.get('message')}"
            )

        object = response.json()
        group_uuid = object["data"]["id"]
        return group_uuid
