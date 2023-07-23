import json
import os
from pathlib import Path
import sys

from database.methods import connect, disconnect, select
from database.schema import *

colours_file = "colours.json"
brands_file = "brands.json"


def expose_brands(file: Path | str, cur):
    rows = select(cur, ["parent", "atoc", "endpoints"], brand_table)
    brands_dict: dict = {}
    for row in rows:
        brand = {"atoc": row[1], "endpoints": row[2]}
        if row[0] in brands_dict:
            brands_dict[row[0]].append(brand)
        else:
            brands_dict[row[0]] = [brand]
    with open(file, "w+") as f:
        f.write(json.dumps(brands_dict))


def expose_colours(file: Path | str, cur):
    rows = select(cur, ["type", "code", "fg", "bg"], colour_table)
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
    expose_brands(root_path / brands_file, cur)
    disconnect(conn, cur)


if __name__ == "__main__":
    expose_all(sys.argv[1])
