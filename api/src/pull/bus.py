import csv
import os
import string

from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from convertbng.util import convert_lonlat  # type: ignore

from pull.core import download_binary, data_directory

################################################################################
#
# NAPTAN
#
# NAPTAN is a data feed published as part of the Open Bus Data Service detailing
# all bus stops across Great Britain.
#
################################################################################


def get_naptan_data_url() -> str:
    return "https://beta-naptan.dft.gov.uk/Download/National/csv"


naptan_path = data_directory / "naptan.csv"


def download_naptan():
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    naptan_url = get_naptan_data_url()
    download_binary(naptan_url, naptan_path)


# naptan columns
atco = 0
naptan = 1
name = 4
landmark = 8
street = 10
indicator = 14
bearing = 16
locality = 18
parent = 19
east = 27
north = 28
lat = 29
lon = 30

################################################################################
# BusStop
################################################################################


@dataclass
class BusStop:
    atco: str
    naptan: Optional[str]
    name: str
    locality: str
    parent: str
    landmark: Optional[str]
    street: str
    indicator: Optional[str]
    bearing: Optional[str]
    lat: float
    lon: float


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
    "After": "after",
    "Opp": "opp",
    "Adj": "adj",
}
redundant_prefixes = ["Stop", "stop", "stand", "Stand", "bay", "platform"]


def read_naptan() -> list[BusStop]:
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
            stop_name = string.capwords(row[name])
            stop_street = string.capwords(row[street])
            stop_landmark = string.capwords(row[landmark])
            stop_locality = row[locality]
            stop_parent = row[parent]
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
                stop_atco,
                stop_naptan,
                stop_name,
                stop_locality,
                stop_parent,
                stop_landmark,
                stop_street,
                stop_trimmed,
                stop_bearing,
                stop_lat,
                stop_lon,
            )
            stops.append(stop)
    return stops
