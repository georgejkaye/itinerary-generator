from typing import Dict, List, Optional
from arrow import Arrow
import arrow
from bs4 import BeautifulSoup
from credentials import Credentials

from request import get_json, get_json_from_api, get_or_throw, get_page

from train.structs import Toc, TrainService, TrainServiceStop, TrainStation, TrainStop
from train.urls import get_train_service_url


def get_train_service_api_endpoint(id: str, run_date: Arrow) -> str:
    date_string = run_date.format("YYYY/MM/DD")
    return f"https://api.rtt.io/api/v1/json/service/{id}/{date_string}"


def get_train_service_json(
    id: str, date: Arrow, credentials: Credentials
) -> Optional[dict]:
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


def arrow_or_none(opt: Optional[str]) -> Optional[Arrow]:
    if opt == "" or opt is None:
        return None
    return arrow.get(opt)


def make_train_service(id: str, date: Arrow) -> Optional[TrainService]:
    service_json = get_json_from_api(
        f"train/service/{id}/{date.year}/{date.month}/{date.day}"
    )
    if service_json is None:
        return None
    origins = list(
        map(
            lambda ep: TrainStation(
                ep["name"], ep["crs"], ep["lat"], ep["lon"], ep["operator"]["name"]
            ),
            service_json["origins"],
        )
    )
    destinations = list(
        map(
            lambda ep: TrainStation(
                ep["name"], ep["crs"], ep["lat"], ep["lon"], ep["operator"]["name"]
            ),
            service_json["destinations"],
        )
    )
    stops = list(
        map(
            lambda stop: TrainServiceStop(
                TrainStop(
                    TrainStation(
                        stop["station"]["name"],
                        stop["station"]["crs"],
                        stop["station"]["lat"],
                        stop["station"]["lon"],
                        Toc(
                            stop["station"]["operator"]["name"],
                            stop["station"]["operator"]["atoc"],
                            stop["station"]["operator"]["fg"],
                            stop["station"]["operator"]["bg"],
                        ),
                    ),
                    stop["platform"],
                ),
                arrow_or_none(stop["plan_arr"]),
                arrow_or_none(stop["plan_dep"]),
            ),
            service_json["stops"],
        )
    )
    operator = Toc(
        service_json["operator"]["name"],
        service_json["operator"]["atoc"],
        service_json["operator"]["fg"],
        service_json["operator"]["bg"],
    )
    return TrainService(
        id,
        service_json["headcode"],
        arrow.get(service_json["run_datetime"]),
        origins,
        destinations,
        stops,
        operator,
    )
