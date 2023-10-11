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
