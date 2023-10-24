import json
from unittest.mock import MagicMock


def json_response(status_code=200, content=""):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json.loads(content)
    return mock_response


def invite_response_invalid_email():
    return json_response(
        400,
        """{
    "ok": false,
    "error": "validation_error",
    "status": 400,
    "message": "email: Invalid email"
}""",
    )


def invite_response_ok():
    return json_response(
        200,
        """{
    "data": {
        "sent": [
            {
                "email": "tarik.ota@test.gouv.fr",
                "name": "Tarik Ota",
                "role": "member"
            }
        ],
        "users": [
            {
                "id": "26985a73-9fc5-4c31-839c-51304daf2628",
                "name": "Tarik Ota",
                "avatarUrl": null,
                "color": "#2BC2FF",
                "isAdmin": false,
                "isSuspended": false,
                "isViewer": false,
                "createdAt": "2023-10-24T14:45:51.889Z",
                "updatedAt": "2023-10-24T14:45:51.889Z",
                "lastActiveAt": null
            }
        ]
    },
    "status": 200,
    "ok": true
}""",
    )


def invite_response_already_invited():
    return json_response(
        200,
        """{
    "data": {
        "sent": [],
        "users": []
    },
    "status": 200,
    "ok": true
}""",
    )


def list_response_ok():
    return json_response(
        200,
        """
    {
  "data": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "Prudence Crandall",
      "avatarUrl": "https://upload.wikimedia.org/wikipedia/commons/0/0d/Appletons%27_Crandall_Prudence.jpg",
      "email": "prudence.crandall@fictif.gouv.fr",
      "isAdmin": true,
      "isSuspended": false,
      "lastActiveAt": "1890-01-28T17:18:22Z",
      "createdAt": "1803-09-03T14:15:22Z"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 25
  }
}""",
    )


def group_creation_ok():
    return json_response(
        200,
        """
    {
    "data": {
        "id": "29907d66-d23f-46e9-be9b-92e2820b81aa",
        "name": "Ce groupe aussi a été créé par API",
        "memberCount": 0,
        "createdAt": "2023-10-19T14:42:40.142Z",
        "updatedAt": "2023-10-19T14:42:40.142Z"
    },
    "policies": [
        {
            "id": "29907d66-d23f-46e9-be9b-92e2820b81aa",
            "abilities": {
                "read": true,
                "update": true,
                "delete": true
            }
        }
    ],
    "status": 200,
    "ok": true
}
    """,
    )


def group_creation_ko_already_exists():
    return json_response(
        400,
        """
    {
    "ok": false,
    "error": "validation_error",
    "status": 400,
    "message": "The name of this group is already in use (isUniqueNameInTeam)"
}
    """,
    )
