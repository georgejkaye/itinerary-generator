from datetime import date, datetime
from typing import Dict, List, Optional, Tuple
from bs4 import BeautifulSoup
from credentials import Credentials

from request import get_json, get_page
from train.structs import ServiceStop, TrainService, TrainStation, TrainStop


def get_train_service_api_endpoint(id: str, date: date) -> str:
    date_string = datetime.strftime(date, "%Y/%m/%d")
    return f"https://api.rtt.io/api/v1/json/service/{id}/{date_string}"


def get_train_service_url(id: str, date: date) -> str:
    date_string = datetime.strftime(date, "%Y-%m-%d")
    return f"https://www.realtimetrains.co.uk/service/gb-nr:{id}/{date_string}/detailed"


def get_train_service_json(id: str, date: date, credentials: Credentials) -> dict:
    json_url = get_train_service_api_endpoint(id, date)
    return get_json(json_url, credentials=credentials)


def get_train_service_page(id: str, date: date) -> BeautifulSoup:
    page_url = get_train_service_url(id, date)
    return get_page(page_url)


def get_endpoint_details(endpoints: List[dict]) -> List[str]:
    endpoint_details = []
    for point in endpoints:
        endpoint_details.append(point["tiploc"])
    return endpoint_details


def get_optional_time(location: dict, key: str, date: date) -> Optional[datetime]:
    time_opt = location.get(key)
    if time_opt is None:
        return None
    else:
        return datetime.combine(date, datetime.strptime(time_opt, "%H%M").time())


def get_service_stop(
    location: dict, date: date, crs_lookup: Dict[str, TrainStation]
) -> ServiceStop:
    stop_crs = location["crs"]
    station = crs_lookup[stop_crs]
    platform = location.get("platform")
    train_stop = TrainStop(station, platform)
    arrival = get_optional_time(location, "gbttBookedArrival", date)
    departure = get_optional_time(location, "gbttBookedDeparture", date)
    return ServiceStop(train_stop, arrival, departure)


def get_service_stops(
    locations: List[dict], date: date, crs_lookup: Dict[str, TrainStation]
) -> List[ServiceStop]:
    return list(map(lambda x: get_service_stop(x, date, crs_lookup), locations))


def make_train_service(
    id: str,
    date: date,
    credentials: Credentials,
    crs_lookup: Dict[str, TrainStation],
) -> TrainService:
    service_dict = get_train_service_json(id, date, credentials)
    service_headcode = service_dict["trainIdentity"]
    service_origins = get_endpoint_details(service_dict["origin"])
    service_destinations = get_endpoint_details(service_dict["destination"])
    first_origin_time = datetime.strptime(
        service_dict["origin"][0]["publicTime"], "%H%M"
    )
    service_datetime = datetime.combine(date, first_origin_time.time())
    service_stops = get_service_stops(service_dict["locations"], date, crs_lookup)
    return TrainService(
        service_headcode,
        service_origins,
        service_destinations,
        service_datetime,
        service_stops,
    )
