import gzip
import json
import os
from pathlib import Path
import shutil
from typing import Dict, Optional, TypeVar
from credentials import Credentials
from request import make_request

data_directory = Path("data")
colours_dir = data_directory / "colours"


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


T = TypeVar("T")


def write_lookup(lookup: Dict[str, T], file: str | Path):
    lookup_dict = {}
    for key in lookup:
        lookup_dict[key] = lookup[key].to_dict()  # type: ignore
    with open(file, "w") as f:
        f.write(json.dumps(lookup_dict))


def record_colours(file: str, bg_colour: str, fg_colour: str):
    if not os.path.exists(colours_dir):
        os.makedirs(colours_dir)
    colour_file = colours_dir / file
    with open(colour_file, "w+") as f:
        f.write(bg_colour)
        f.write("\n")
        f.write(fg_colour)
