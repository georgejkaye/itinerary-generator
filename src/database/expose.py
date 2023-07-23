import json
import os
from pathlib import Path
import sys

from database.select import select
from database.connection import connect, disconnect
from database.schema import *

colours_file = "colours.json"


def expose_colours(file: Path | str, cur):
    rows = select(cur, ["type", "code", "fg", "bg"], colours_table)
    train_colours = {}
    bus_colours = {}
    for row in rows:
        code = row[1]
        colours = {"fg": row[2], "bg": row[3]}
        if row[0] == "train":
            train_colours[code] = colours
        elif row[1] == "bus":
            bus_colours[code] = colours
    colours_dict = {"train": train_colours, "bus": bus_colours}
    with open(file, "w+") as f:
        f.write(json.dumps(colours_dict))


def expose_all(root: Path | str):
    (conn, cur) = connect()
    root_path = Path(root)
    if not os.path.isdir(root_path):
        os.makedirs(root_path)
    expose_colours(root_path / colours_file, cur)
    disconnect(conn, cur)
