from json import JSONDecodeError
from dotenv import dotenv_values
import requests

from typing import Optional, TypeVar
from bs4 import BeautifulSoup, ResultSet, Tag
from requests import Response
from requests.auth import HTTPBasicAuth

from credentials import Credentials

T = TypeVar("T")


def get_or_throw(t: Optional[T]) -> T:
    if t is None:
        raise RuntimeError("Expected Some but got None")
    return t


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
) -> Optional[dict]:
    response = make_request(url, credentials=credentials)
    if response.status_code == 200:
        try:
            return response.json()
        except JSONDecodeError:
            return None
    else:
        return None


env_variables = dotenv_values()
api_host = env_variables["API_HOST"]


def get_json_from_api(endpoint: str) -> Optional[dict]:
    url = f"{api_host}/{endpoint}"
    return get_json(url)


def get_page(url: str, credentials: Optional[Credentials] = None) -> BeautifulSoup:
    page = make_request(url, credentials)
    return BeautifulSoup(page.content, "html.parser")


def select_one(soup: BeautifulSoup | Tag, selector: str) -> Tag:
    result = soup.select_one(selector)
    if result is None:
        raise RuntimeError(f"No matches for {selector}")
    return result


def select_all(soup: BeautifulSoup | Tag, selector: str) -> ResultSet[Tag]:
    result = soup.select(selector)
    if result is None:
        raise RuntimeError(f"No matches for {selector}")
    return result


def get_href(tag: Tag) -> str:
    href = tag.get_attribute_list("href")
    if href is None:
        raise RuntimeError(f"No href in {tag}")
    return href[0]


def get_id(tag: Tag) -> str:
    id = tag.get_attribute_list("id")
    if id is None:
        raise RuntimeError(f"No id in {tag}")
    return id[0]
