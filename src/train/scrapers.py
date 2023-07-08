from typing import Dict, List, Optional
from arrow import Arrow
import arrow
from bs4 import BeautifulSoup
from credentials import Credentials

from request import get_json, get_page
from train.structs import TrainService, TrainServiceStop, TrainStation, TrainStop
from train.urls import get_train_service_url


def get_train_service_api_endpoint(id: str, run_date: Arrow) -> str:
    date_string = run_date.format("YYYY/MM/DD")
    return f"https://api.rtt.io/api/v1/json/service/{id}/{date_string}"


def get_train_service_json(id: str, date: Arrow, credentials: Credentials) -> dict:
    json_url = get_train_service_api_endpoint(id, date)
    return get_json(json_url, credentials=credentials)


def get_train_service_page(id: str, date: Arrow) -> BeautifulSoup:
    page_url = get_train_service_url(id, date)
    return get_page(page_url)


def get_endpoint_details(endpoints: List[dict]) -> List[str]:
    endpoint_details = []
    for point in endpoints:
        endpoint_details.append(point["description"])
    return endpoint_details


def get_optional_time(location: dict, key: str, date: Arrow) -> Optional[Arrow]:
    time_opt = location.get(key)
    if time_opt is None:
        return None
    else:
        time = arrow.get(time_opt, "HHmm")
        return arrow.get(date.year, date.month, date.day, time.hour, time.minute)


def get_service_stop(
    location: dict, date: Arrow, crs_lookup: Dict[str, TrainStation]
) -> TrainServiceStop:
    stop_crs = location["crs"]
    station = crs_lookup[stop_crs]
    platform = location.get("platform")
    train_stop = TrainStop(station, platform)
    arrival = get_optional_time(location, "gbttBookedArrival", date)
    departure = get_optional_time(location, "gbttBookedDeparture", date)
    return TrainServiceStop(train_stop, arrival, departure)


def get_service_stops(
    locations: List[dict], date: Arrow, crs_lookup: Dict[str, TrainStation]
) -> List[TrainServiceStop]:
    stops = []
    for loc in locations:
        if loc["isCall"]:
            stop = get_service_stop(loc, date, crs_lookup)
            stops.append(stop)
    return stops


def make_train_service(
    id: str,
    date: Arrow,
    credentials: Credentials,
    crs_lookup: Dict[str, TrainStation],
) -> TrainService:
    service_dict = get_train_service_json(id, date, credentials)
    service_headcode = service_dict["trainIdentity"]
    service_operator = service_dict["atocName"]
    service_origins = get_endpoint_details(service_dict["origin"])
    service_destinations = get_endpoint_details(service_dict["destination"])
    first_origin_time = arrow.get(service_dict["origin"][0]["publicTime"], "HHmm")
    service_datetime = arrow.get(
        date.year,
        date.month,
        date.day,
        first_origin_time.hour,
        first_origin_time.minute,
    )
    service_stops = get_service_stops(service_dict["locations"], date, crs_lookup)
    return TrainService(
        id,
        service_headcode,
        service_origins,
        service_destinations,
        service_datetime,
        service_stops,
        service_operator,
    )
