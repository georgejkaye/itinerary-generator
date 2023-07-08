from datetime import timedelta
from pathlib import Path
from typing import List
from arrow import Arrow
from jinja2 import Environment, FileSystemLoader, select_autoescape

from structs import Segment, get_duration_string


def ampersand(input: List[str]):
    return " & ".join(input)


def colon_time(input: Arrow):
    return input.format("HH:mm")


def military_time(input: Arrow):
    return input.format("HHmm")


def hours_minutes(input: timedelta):
    return get_duration_string(input)


def write_output(segments: List[Segment], output_file: Path | str):
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
    with open(output_file, "w") as file:
        file.write(html)
