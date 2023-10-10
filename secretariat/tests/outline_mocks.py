import json
from unittest.mock import MagicMock


def json_response(status_code=200, content=""):
    mock_response = MagicMock()
    mock_response.status_code = status_code
    mock_response.json.return_value = json.loads(content)
    return mock_response


def list_response_ok():
    return json_response(
        200,
        """
    {
  "data": [
    {
      "id": "497f6eca-6276-4993-bfeb-53cbbbba6f08",
      "name": "Jane Doe",
      "avatarUrl": "http://example.com",
      "email": "user@example.com",
      "isAdmin": true,
      "isSuspended": true,
      "lastActiveAt": "2019-08-24T14:15:22Z",
      "createdAt": "2019-08-24T14:15:22Z"
    }
  ],
  "pagination": {
    "offset": 0,
    "limit": 25
  }
}""",
    )
