from typing import Dict

import arrow
from bus.scrapers import get_bus_trip, get_bus_trip_segment
from credentials import Credentials
from structs import Segment
from train.scrapers import make_train_service
from train.structs import TrainService, TrainStation


def parse_bus_element(item: dict) -> Segment:
    date = arrow.get(item["date"])
    id = int(item["id"])
    board = item["board"]
    alight = item["alight"]
    trip = get_bus_trip(date, id)
    segment = get_bus_trip_segment(trip, board, alight)
    if segment is None:
        raise RuntimeError("Not a valid segment")
    return segment


def read_train_element(
    element: dict, rtt_credentials: Credentials, crs_lookup: Dict[str, TrainStation]
) -> TrainService:
    id = element["id"]
    date = element["date"]
    origin = element["origin"]
    destination = element["destination"]
    return make_train_service(id, date, rtt_credentials, crs_lookup)
