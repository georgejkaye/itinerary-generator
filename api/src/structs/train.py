from re import S
from typing import Optional
import xml.etree.ElementTree as ET

from dataclasses import dataclass
from database.methods import select

from pull.core import get_or_throw, get_tag_text, make_request, prefix_namespace
from pull.train import (
    get_kb_url,
    get_natrail_token_headers,
    kb_stations_namespace,
    kb_tocs_namespace,
)

from database.schema import *


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
class Brand:
    atoc: str
    endpoints: list[str]


@dataclass
class TocData:
    name: str
    atoc: str
    fg: str
    bg: str
    brands: list[Brand]


def select_brands(cur, atoc: str) -> list[Brand]:
    rows = select(
        cur,
        ["atoc", "endpoints"],
        brand_table,
        ["parent = %(parent)s"],
        {"parent": atoc},
    )
    return list(map(lambda row: Brand(row[0], row[1]), rows))


def select_toc(cur, atoc: str) -> Optional[TocData]:
    rows = select(
        cur,
        ["toc.name", "toc.atoc", "colour.fg", "colour.bg"],
        f"{toc_table} LEFT OUTER JOIN {colour_table} ON toc.atoc = colour.code",
        ["atoc = %(atoc)s"],
        {"atoc": atoc},
    )
    if len(rows) != 1:
        return None
    else:
        row = rows[0]
        brands = select_brands(cur, atoc)
        return TocData(row[0], row[1], row[2], row[3], brands)


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
class TrainStationData:
    name: str
    crs: str
    lat: float
    lon: float
    operator: Toc


def select_train_station(cur, descriptor: str) -> Optional[TrainStationData]:
    rows = select(
        cur,
        ["crs", "name", "lat", "lon", "operator"],
        train_station_table,
        ["crs = %(desc)s OR name = %(desc)s"],
        {"desc": descriptor},
    )
    if len(rows) != 1:
        return None
    else:
        row = rows[0]
        operator = get_or_throw(select_toc(cur, row[4]))
        return TrainStationData(row[0], row[1], row[2], row[3], operator)
