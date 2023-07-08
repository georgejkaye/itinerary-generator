from datetime import timedelta
import os
from pathlib import Path
import shutil
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


def write_output(segments: List[Segment], output_path: Path | str):
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
    html_path = Path(output_path) / "index.html"
    os.makedirs(output_path, exist_ok=True)
    with open(html_path, "w") as file:
        file.write(html)
    output_css_path = Path(output_path) / "styles.css"
    shutil.copyfile(css_path, output_css_path)
