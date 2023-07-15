from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Dict, List
from bus.structs import BusStop
from data import download_binary, data_directory, write_lookup
import csv
from convertbng.util import convert_lonlat  # type: ignore


def get_naptan_data_url() -> str:
    return "https://beta-naptan.dft.gov.uk/Download/National/csv"


naptan_path = data_directory / "naptan.csv"
bus_stop_path = data_directory / "bus-stops.json"
atco_lookup_path = data_directory / "atco-lookup.json"
bus_directory = data_directory / "bus"


def download_naptan():
    naptan_url = get_naptan_data_url()
    download_binary(naptan_url, naptan_path)


# naptan columns
atco = 0
naptan = 1
name = 4
indicator = 14
bearing = 16
east = 27
north = 28
lat = 29
lon = 30


def trim_indicator_prefixes(prefixes: list[str], indicator: str) -> str:
    for prefix in prefixes:
        length = len(prefix)
        if indicator[0:length] == prefix:
            return indicator[length:]
    return indicator


def replace_indicator(replacements: dict[str, str], indicator: str) -> str:
    for key, val in replacements.items():
        if key in indicator:
            return indicator.replace(key, val)
    return indicator


replacements = {
    "adjacent": "adj",
    "opposite": "opp",
    "outside": "o/s",
    "near": "nr",
    "corner": "cnr",
}
redundant_prefixes = ["Stop", "stand", "bay", "platform"]


def read_naptan() -> List[BusStop]:
    stops = []
    with open(naptan_path, "r") as f:
        rows = csv.reader(f, delimiter=",")
        # skip the header row
        next(rows, None)
        for row in rows:
            stop_atco = row[atco]
            if row[naptan] == "":
                stop_naptan = None
            else:
                stop_naptan = row[naptan]
            stop_name = row[name]
            stop_indicator = row[indicator]
            stop_replaced = replace_indicator(replacements, stop_indicator)
            stop_trimmed = trim_indicator_prefixes(redundant_prefixes, stop_replaced)
            stop_bearing = row[bearing]
            if row[lat] == "" or row[lon] == "":
                stop_east = float(row[east])
                stop_north = float(row[north])
                (lons, lats) = convert_lonlat([stop_east], [stop_north])
                (stop_lat, stop_lon) = (lons[0], lats[0])
            else:
                stop_lat = float(row[lat])
                stop_lon = float(row[lon])
            stop = BusStop(
                stop_name,
                stop_trimmed,
                stop_bearing,
                stop_lat,
                stop_lon,
                stop_naptan,
                stop_atco,
            )
            stops.append(stop)
    return stops


def get_stop_lookup(stops: List[BusStop]) -> Dict[str, BusStop]:
    lookup = {}
    for stop in stops:
        lookup[stop.atco] = stop
    return lookup


def write_stop_lookup(lookup: Dict[str, BusStop], file: str | Path):
    lookup_dict = {}
    for key in lookup:
        lookup_dict[key] = lookup[key].to_dict()  # type: ignore
    with open(file, "w") as f:
        f.write(json.dumps(lookup_dict))


def write_bus_stop_data(stops: List[BusStop], file: str | Path):
    if not os.path.isdir(bus_directory):
        os.makedirs(bus_directory)
    total = len(stops)
    for i, stop in enumerate(stops):
        print(f"writing {i}/{total}: {stop.atco}")
        json = BusStop.schema().dumps(stop)  # type: ignore
        path = bus_directory / stop.atco
        with open(path, "w") as f:
            f.write(json)


def read_stop_data(file: str | Path) -> List[BusStop]:
    with open(file, "r") as f:
        stop_json = f.read()
    return BusStop.schema().loads(stop_json, many=True)  # type: ignore


def read_stop_lookup(file: str | Path) -> Dict[str, BusStop]:
    with open(file, "r") as f:
        data = json.loads(f.read())
    stop_dict = {}
    for key in data:
        stop_dict[key] = BusStop.from_dict(data[key])  # type: ignore
    return stop_dict


@dataclass
class BusData:
    atco_lookup: Dict[str, BusStop]


def setup_bus_data():
    if not os.path.isdir(data_directory):
        os.makedirs(data_directory)
    if not os.path.isfile(naptan_path):
        download_naptan()
    stops = read_naptan()
    # lookup = get_stop_lookup(stops)
    write_bus_stop_data(stops, bus_stop_path)
    # write_lookup(lookup, atco_lookup_path)
    # return BusData(lookup)


def read_bus_data() -> BusData:
    # stops = read_stop_data(bus_stop_path)
    lookup = read_stop_lookup(atco_lookup_path)
    return BusData(lookup)


def get_bus_stop_json(atco: str) -> dict:
    path = bus_directory / atco
    with open(path, "r") as f:
        data = json.load(f)
    return data
