import requests

from config.settings import OUTLINE_API_TOKEN, OUTLINE_URL
from secretariat.models import User


class OutlineAPIClientError(Exception):
    def __init__(self, error_code, error_message=""):
        self.status_code = error_code
        self.error_message = error_message


class RemoteServerError(OutlineAPIClientError):
    pass


class InvalidRequest(OutlineAPIClientError):
    pass


class InvitationFailed(OutlineAPIClientError):
    pass


class GroupCreationFailed(OutlineAPIClientError):
    pass


class Client:
    url = OUTLINE_URL
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": f"Bearer {OUTLINE_API_TOKEN}",
    }

    def invite_to_outline(self, user: User):
        response = requests.post(
            url=f"{self.url}/api/users.invite",
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
        if response.status_code == 400:
            object = response.json()
            raise InvalidRequest(
                400, f"{object.get('error')} - {object.get('message')}"
            )

        if response.status_code >= 500:
            raise RemoteServerError(response.status_code)

        if len(response.json()["data"]["users"]) == 0:
            raise InvitationFailed(response.status_code)

        user_uuid = response.json()["data"]["users"][0]["id"]
        return user_uuid

    def add_to_outline_group(self, user_uuid, group_uuid):
        requests.post(
            url=f"{self.url}/api/groups.add_user",
            headers=self.headers,
            json={
                "id": group_uuid,
                "userId": user_uuid,
            },
        )

    def list_users(self, query=""):
        response = requests.post(
            url=f"{self.url}/api/users.list",
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

    def find_user_from_email(self, email):
        response = requests.post(
            url=f"{self.url}/api/users.list",
            headers=self.headers,
            json={
                "offset": 0,
                "limit": 1,
                "emails": [email],
            },
        )
        if response.status_code != 200:
            raise RemoteServerError(response.status_code)

        return response.json()["data"][0]

    def create_new_group(self, group_name):
        response = requests.post(
            url=f"{self.url}/api/groups.create",
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

    def list_groups(self, offset=0, limit=25):
        response = requests.post(
            url=f"{OUTLINE_API_URL}/groups.list",
            headers=self.headers,
            json={
                "offset": offset,
                "limit": limit,
                "sort": "createdAt",
                "direction": "ASC",
            },
        )
        if response.status_code >= 500:
            raise RemoteServerError(response.status_code)
        object = response.json()
        return object.get("data").get("groups")

    def find_group_by_name(self, group_name):
        offset = 0
        step = 20
        list = self.list_groups(offset, step)
        matching_groups = [group for group in list if group["name"] == group_name]

        while len(list) and not (len(matching_groups)):
            offset += step
            list = self.list_groups(offset, step)
            matching_groups = [group for group in list if group["name"] == group_name]

        if len(matching_groups):
            return matching_groups[0]

    def remove_user_from_outline(self, user: User):
        requests.post(
            url=f"{self.url}/api/users.delete",
            headers=self.headers,
            json={
                "id": user.outline_uuid,
            },
        )
