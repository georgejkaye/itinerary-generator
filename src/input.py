from typing import Callable, Dict, Tuple

import arrow
from bus.scrapers import get_bus_trip
from bus.structs import BusStop
from credentials import Credentials
from structs import Segment, TripInterface, get_segment
from train.scrapers import make_train_service
from train.structs import TrainService, TrainStation
from walk.scraper import get_direction_stats
from walk.structs import WalkPoint, WalkStop, WalkTrip


def get_colours(item: dict) -> Tuple[str, str, str]:
    colour = item.get("colour")
    if colour is None:
        fg_colour = "#ffffff"
        bg_colour = "#000000"
        border_colour = "#000000"
    else:
        if colour.get("fg") is None:
            fg_colour = "#ffffff"
        else:
            fg_colour = colour["fg"]
        if colour.get("bg") is None:
            bg_colour = "#000000"
        else:
            bg_colour = colour["bg"]
        border_colour = colour.get("border")
    return (fg_colour, bg_colour, border_colour)


def parse_bus_element(item: dict) -> Segment:
    date = arrow.get(item["date"])
    id = int(item["id"])
    board = item["board"]
    alight = item["alight"]
    (fg_colour, bg_colour, border_colour) = get_colours(item)
    trip = get_bus_trip(date, id)
    segment = get_segment(trip, board, alight, fg_colour, bg_colour, border_colour)
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
    (fg_colour, bg_colour, border_colour) = get_colours(element)
    trip = make_train_service(id, date, rtt_credentials, crs_lookup)
    segment = get_segment(trip, board, alight, fg_colour, bg_colour, border_colour)
    if segment is None:
        raise RuntimeError("Not a valid segment")
    return segment


def parse_walk_element(item: dict) -> Segment:
    start_dict = item["start"]
    start_name = start_dict["name"]
    start_lat = start_dict["lat"]
    start_lon = start_dict["lon"]
    start_time = arrow.get(start_dict["time"])
    start = WalkPoint(start_name, start_lat, start_lon)
    start_stop = WalkStop(start, start_time)
    finish_dict = item["finish"]
    finish_name = finish_dict["name"]
    finish_lat = finish_dict["lat"]
    finish_lon = finish_dict["lon"]
    finish = WalkPoint(finish_name, finish_lat, finish_lon)
    (distance, duration) = get_direction_stats(
        start_lat, start_lon, finish_lat, finish_lon
    )
    finish_stop = WalkStop(finish, start_time.shift(seconds=duration))
    trip = WalkTrip(start_stop, finish_stop, duration, distance)
    return Segment(trip, 0, 1, "#ffffff", "#000000", "#000000")
