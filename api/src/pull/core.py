import gzip
import os
import shutil

from pathlib import Path
from typing import Optional, TypeVar
from dotenv import dotenv_values
from credentials import Credentials

from pull.request import make_request


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
