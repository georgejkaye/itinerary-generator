import json
from typing import Optional
from bs4 import BeautifulSoup, ResultSet, Tag
import requests
from requests import Response
from requests.auth import HTTPBasicAuth

from credentials import Credentials


def make_request(
    url: str, credentials: Optional[Credentials] = None, stream: bool = False
) -> Response:
    if credentials is not None:
        auth = HTTPBasicAuth(credentials.user, credentials.password)
    else:
        auth = None
    return requests.get(url, auth=auth, stream=stream)


def get_json(url: str, credentials: Optional[Credentials] = None) -> dict:
    return make_request(url, credentials=credentials).json()


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
