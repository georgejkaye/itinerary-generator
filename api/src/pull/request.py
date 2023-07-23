import requests

from typing import Optional

from requests import Response
from requests.auth import HTTPBasicAuth

from credentials import Credentials


def make_request(
    url: str,
    credentials: Optional[Credentials] = None,
    stream: bool = False,
    headers: Optional[dict] = None,
) -> Response:
    if credentials is not None:
        auth = HTTPBasicAuth(credentials.user, credentials.password)
    else:
        auth = None
    print(f"Making request to {url}")
    return requests.get(url, auth=auth, stream=stream, headers=headers)


def get_json(
    url: str, credentials: Optional[Credentials] = None, headers: Optional[dict] = None
) -> dict:
    return make_request(url, credentials=credentials).json()


def make_post_request(
    url: str, headers: Optional[dict] = None, data: Optional[dict] = None
) -> Response:
    print(f"Making post request to {url}")
    return requests.post(url, headers=headers, data=data)


def get_post_json(
    url: str, headers: Optional[dict] = None, data: Optional[dict] = None
) -> dict:
    response = make_post_request(url, headers, data)
    if response.status_code != 200:
        print(f"Error {response.status_code} received")
        exit(1)
    else:
        return response.json()
