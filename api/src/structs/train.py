import xml.etree.ElementTree as ET

from dataclasses import dataclass
from database.methods import select

from pull.core import get_tag_text, make_request, prefix_namespace
from pull.train import (
    get_kb_url,
    get_natrail_token_headers,
    kb_stations_namespace,
    kb_tocs_namespace,
)

from database.schema import *


@dataclass
class TrainStation:
    name: str
    crs: str
    lat: float
    lon: float
    operator: str


def pull_stations(natrail_token: str) -> list[TrainStation]:
    kb_stations_url = get_kb_url("stations")
    headers = get_natrail_token_headers(natrail_token)
    kb_stations = make_request(kb_stations_url, headers=headers).text
    kb_stations_xml = ET.fromstring(kb_stations)
    stations = []
    for stn in kb_stations_xml.findall(
        prefix_namespace(kb_stations_namespace, "Station")
    ):
        station_name = get_tag_text(stn, "Name", kb_stations_namespace)
        station_crs = get_tag_text(stn, "CrsCode", kb_stations_namespace)
        station_lat = float(get_tag_text(stn, "Latitude", kb_stations_namespace))
        station_lon = float(get_tag_text(stn, "Longitude", kb_stations_namespace))
        station_operator = get_tag_text(stn, "StationOperator", kb_stations_namespace)
        station = TrainStation(
            station_name, station_crs, station_lat, station_lon, station_operator
        )
        stations.append(station)
    return stations


@dataclass
class Toc:
    name: str
    atoc: str


def pull_tocs(natrail_token: str) -> list[Toc]:
    kb_tocs_url = get_kb_url("tocs")
    headers = get_natrail_token_headers(natrail_token)
    kb_tocs = make_request(kb_tocs_url, headers=headers).text
    kb_tocs_xml = ET.fromstring(kb_tocs)
    tocs = []
    for toc in kb_tocs_xml.findall(
        prefix_namespace(kb_tocs_namespace, "TrainOperatingCompany")
    ):
        toc_name = get_tag_text(toc, "Name", kb_tocs_namespace)
        toc_code = get_tag_text(toc, "AtocCode", kb_tocs_namespace)
        tocs.append(Toc(toc_name, toc_code))
    return tocs


@dataclass
class TocWithColours:
    name: str
    atoc: str
    fg: str
    bg: str


def select_toc(cur, atoc: str) -> TocWithColours:
    rows = select(
        cur,
        ["toc.name", "toc.atoc", "colour.fg", "colour.bg"],
        f"{toc_table} INNER JOIN {colour_table} ON toc.atoc = colour.code",
        ["atoc = %(atoc)s"],
        {"atoc": atoc},
    )
    if len(rows) != 1:
        raise RuntimeError(f"No match for atoc {atoc}")
    else:
        row = rows[0]
        return TocWithColours(row[0], row[1], row[2], row[3])
