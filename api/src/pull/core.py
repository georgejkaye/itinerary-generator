import xml.etree.ElementTree as ET
import gzip
import os
import shutil
import requests

from pathlib import Path
from typing import Any, Optional, TypeVar
from dotenv import dotenv_values
from requests import Response
from requests.auth import HTTPBasicAuth

from credentials import Credentials

T = TypeVar("T")


def get_or_throw(t: Optional[T]) -> T:
    if t is None:
        raise RuntimeError("Expected Some but got None")
    return t


env_values = dotenv_values()
data_dir = get_or_throw(env_values.get("DATA_DIR"))

data_directory = Path(data_dir)


def extract_gz(gz_path: str | Path, output_path: str | Path):
    with gzip.open(gz_path, "rb") as f:
        with open(output_path, "wb") as out:
            shutil.copyfileobj(f, out)
    os.remove(gz_path)


def download_binary(url: str, path: str, credentials: Optional[Credentials] = None):
    response = make_request(url, credentials=credentials, stream=True)
    if response.status_code != 200:
        raise RuntimeError(f"Could not get {url}")
    with open(path, "wb+") as f:
        f.write(response.raw.read())


def prefix_namespace(namespace: str, tag: str) -> str:
    return f"{{{namespace}}}{tag}"


def get_tag_text(root: ET.Element, tag: str, namespace: Optional[str] = None) -> str:
    if namespace is not None:
        tag = prefix_namespace(namespace, tag)
    content: Any = get_or_throw(root.find(tag))
    return get_or_throw(content.text)


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
