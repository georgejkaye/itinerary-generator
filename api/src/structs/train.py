from re import S
from typing import Optional
import xml.etree.ElementTree as ET

import arrow
from fastapi import HTTPException
from pydantic import BaseModel, ConfigDict, validator
from pydantic.dataclasses import dataclass

from arrow import Arrow
from credentials import Credentials
from database.methods import select, select_query
from pull import train

from pull.core import (
    get_json,
    get_or_throw,
    get_tag_text,
    make_request,
    prefix_namespace,
)
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
class TocDataSlimline:
    name: str
    atoc: str
    fg: str
    bg: str


@dataclass
class TocData:
    name: str
    atoc: str
    fg: str
    bg: str
    brands: list[Brand]

    def to_slimline(self) -> TocDataSlimline:
        return TocDataSlimline(self.name, self.atoc, self.fg, self.bg)


def select_brands(cur, atoc: str) -> list[Brand]:
    rows = select(
        cur,
        ["atoc", "endpoints"],
        brand_table,
        ["parent = %(parent)s"],
        {"parent": atoc},
    )
    return list(map(lambda row: Brand(row[0], row[1]), rows))


def select_toc(cur, descriptor: str) -> Optional[TocData]:
    rows = select(
        cur,
        ["toc.name", "toc.atoc", "colour.fg", "colour.bg"],
        f"{toc_table} LEFT OUTER JOIN {colour_table} ON toc.atoc = colour.code",
        ["atoc = %(descriptor)s or name = %(descriptor)s"],
        {"descriptor": descriptor},
    )
    if len(rows) != 1:
        return None
    else:
        row = rows[0]
        brands = select_brands(cur, row[1])
        return TocData(row[0], row[1], row[2], row[3], brands)


def select_toc_slimline(cur, descriptor: str) -> Optional[TocDataSlimline]:
    toc = select_toc(cur, descriptor)
    if toc is None:
        return None
    return TocDataSlimline(toc.name, toc.atoc, toc.fg, toc.bg)


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
    operator: TocData


@dataclass
class TrainStationDataSlimline:
    name: str
    crs: str
    lat: float
    lon: float
    operator: TocDataSlimline


def select_train_station(cur, descriptor: str) -> Optional[TrainStationDataSlimline]:
    statement = f"""
        SELECT
            {train_station_table}.name,
            {train_station_table}.crs,
            {train_station_table}.lat,
            {train_station_table}.lon,
            {toc_table}.name AS operator_name,
            {toc_table}.atoc AS operator_atoc,
            {colour_table}.fg,
            {colour_table}.bg
        FROM
            {train_station_table}
        INNER JOIN
            {toc_table}
        ON
            {train_station_table}.operator = {toc_table}.atoc
        INNER JOIN
            {colour_table}
        ON
            {toc_table}.atoc = {colour_table}.code
        WHERE
            {train_station_table}.name = %(descriptor)s
            OR
            {train_station_table}.crs = %(descriptor)s
    """
    rows = select_query(
        cur,
        statement,
        {"descriptor": descriptor},
    )
    if len(rows) != 1:
        return None
    else:
        row = rows[0]
        return TrainStationDataSlimline(
            row[0],
            row[1],
            row[2],
            row[3],
            TocDataSlimline(row[4], row[5], row[6], row[7]),
        )


@dataclass(config=dict(arbitrary_types_allowed=True))
class TrainServiceStop:
    station: TrainStationDataSlimline
    platform: Optional[str]
    plan_arr: Optional[str]
    plan_dep: Optional[str]


@dataclass(config=dict(arbitrary_types_allowed=True))
class TrainService:
    id: str
    headcode: str
    run_datetime: str
    origins: list[TrainStationDataSlimline]
    destinations: list[TrainStationDataSlimline]
    stops: list[TrainServiceStop]
    operator: TocDataSlimline


def get_train_service_api_endpoint(id: str, run_date: Arrow) -> str:
    date_string = run_date.format("YYYY/MM/DD")
    return f"https://api.rtt.io/api/v1/json/service/{id}/{date_string}"


def get_endpoint_stations(cur, endpoints: list[dict]) -> list[TrainStationDataSlimline]:
    endpoint_stations = []
    for point in endpoints:
        station = select_train_station(cur, point["description"])
        if station is not None:
            endpoint_stations.append(station)
    return endpoint_stations


def get_optional_time(location: dict, key: str, run_date: Arrow) -> Optional[Arrow]:
    time_opt = location.get(key)
    if time_opt is None:
        return None
    else:
        time = arrow.get(time_opt, "HHmm")
        return arrow.get(
            run_date.year, run_date.month, run_date.day, time.hour, time.minute
        )


def format_or_none(arrow_opt: Optional[Arrow]) -> Optional[str]:
    if arrow_opt is None:
        return None
    return arrow_opt.format()


def get_service_stops(
    cur, locations: list[dict], run_date: Arrow
) -> list[TrainServiceStop]:
    stops = []
    calls = filter(lambda loc: loc["isCall"], locations)
    call_codes = list(map(lambda call: call["crs"], calls))
    statement = f"""
        SELECT
            {train_station_table}.name,
            {train_station_table}.crs,
            {train_station_table}.lat,
            {train_station_table}.lon,
            {toc_table}.name AS operator_name,
            {toc_table}.atoc AS operator_atoc,
            {colour_table}.fg AS operator_fg,
            {colour_table}.bg AS operator_bg
        FROM
            {train_station_table}
            INNER JOIN
                (SELECT UNNEST(%(calls)s)) calls
            ON
                {train_station_table}.crs = calls.unnest
            INNER JOIN
                {toc_table}
            ON
                {train_station_table}.operator = {toc_table}.atoc
            INNER JOIN
                {colour_table}
            ON
                {toc_table}.atoc = {colour_table}.code
    """
    rows = select_query(cur, statement, {"calls": call_codes})
    for loc, row in zip(locations, rows):
        plan_arr = get_optional_time(loc, "gbttBookedArrival", run_date)
        plan_dep = get_optional_time(loc, "gbttBookedDeparture", run_date)
        stops.append(
            TrainServiceStop(
                TrainStationDataSlimline(
                    row[0],
                    row[1],
                    row[2],
                    row[3],
                    TocDataSlimline(row[4], row[5], row[6], row[7]),
                ),
                loc.get("platform"),
                format_or_none(plan_arr),
                format_or_none(plan_dep),
            )
        )
    return stops


def pull_service(
    cur, id: str, run_date: Arrow, rtt_credentials: Credentials
) -> Optional[TrainService]:
    endpoint = get_train_service_api_endpoint(id, run_date)
    json = get_json(endpoint, credentials=rtt_credentials)
    if json is None or json.get("error") is not None:
        return None
    headcode = json["trainIdentity"]
    origins = get_endpoint_stations(cur, json["origin"])
    destinations = get_endpoint_stations(cur, json["destination"])
    operator_opt = select_toc(cur, json["atocName"])
    if operator_opt is None:
        raise HTTPException(
            status_code=500, detail=f"Could not find toc {json['atocName']}"
        )
    operator = operator_opt
    if len(operator.brands) > 0:
        found_brand = None
        for brand in operator.brands:
            endpoints = brand.endpoints
            for item in origins:
                if item.name in endpoints:
                    found_brand = brand
                    break
            if found_brand is None:
                for item in destinations:
                    if item.name in endpoints:
                        found_brand = brand
                        break
        if found_brand is None:
            origin_strings = list(map(lambda p: p.name, origins))
            destination_strings = list(map(lambda p: p.name, destinations))
            raise HTTPException(
                status_code=500,
                detail=f"Cannot find brand for origins {origin_strings} or destinations {destination_strings}",
            )
        operator_slimline = get_or_throw(select_toc(cur, brand.atoc)).to_slimline()
    else:
        operator_slimline = operator.to_slimline()
    first_origin_time = arrow.get(json["origin"][0]["publicTime"], "HHmm")
    run_datetime = arrow.get(
        run_date.year,
        run_date.month,
        run_date.day,
        first_origin_time.hour,
        first_origin_time.minute,
    )
    stops = get_service_stops(cur, json["locations"], run_date)
    return TrainService(
        id,
        headcode,
        run_datetime.format(),
        origins,
        destinations,
        stops,
        operator_slimline,
    )
