import os
import shutil

from datetime import timedelta
from pathlib import Path
from typing import List
from arrow import Arrow
from jinja2 import Environment, FileSystemLoader, select_autoescape

from structs import Segment, get_duration_string

assets_dir = Path("assets")
css_path = assets_dir / "styles.css"


def ampersand(input: List[str]):
    return " & ".join(input)


def colon_time(input: Arrow):
    return input.format("HH:mm")


def military_time(input: Arrow):
    return input.format("HHmm")


def hours_minutes(input: timedelta):
    return get_duration_string(input)


def write_output(segments: List[Segment], output: Path | str):
    env = Environment(
        loader=FileSystemLoader("templates"), autoescape=select_autoescape()
    )
    env.filters = {
        **env.filters,
        "ampersand": ampersand,
        "colon_time": colon_time,
        "military_time": military_time,
        "hours_minutes": hours_minutes,
    }
    index = env.get_template("index.html")
    html = index.render(segments=segments)
    output_path = Path(output)
    html_path = output_path / "index.html"
    # delete any previous build
    if os.path.exists(output_path):
        resp = input(f"File or directory {output_path} exists, delete? (y/N) ")
        if resp == "y":
            shutil.rmtree(output_path)
        else:
            exit(1)
    os.makedirs(output_path)
    with open(html_path, "w") as file:
        file.write(html)
    output_assets_dir = output_path / "assets"
    shutil.copytree(assets_dir, output_assets_dir)
