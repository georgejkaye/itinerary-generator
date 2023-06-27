from typing import Dict

import arrow
from bus.scrapers import get_bus_trip
from credentials import Credentials
from structs import Segment, get_segment
from train.scrapers import make_train_service
from train.structs import TrainService, TrainStation


def parse_bus_element(item: dict) -> Segment:
    date = arrow.get(item["date"])
    id = int(item["id"])
    board = item["board"]
    alight = item["alight"]
    trip = get_bus_trip(date, id)
    segment = get_segment(trip, board, alight)
    if segment is None:
        raise RuntimeError("Not a valid segment")
    return segment


def parse_train_element(
    element: dict, rtt_credentials: Credentials, crs_lookup: Dict[str, TrainStation]
) -> Segment:
    id = element["id"]
    date = arrow.get(element["date"])
    board = element["board"]
    alight = element["alight"]
    trip = make_train_service(id, date, rtt_credentials, crs_lookup)
    segment = get_segment(trip, board, alight)
    if segment is None:
        raise RuntimeError("Not a valid segment")
    return segment
