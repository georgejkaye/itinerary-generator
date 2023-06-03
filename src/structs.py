from dataclasses import dataclass
from datetime import time, timedelta
from typing import List, Optional


@dataclass
class BusStop:
    name: str
    platform: Optional[str]
    lat: float
    lon: float
    naptan: str
    atco: str


@dataclass
class BusStopWindow:
    stop: BusStop
    time: time


@dataclass
class BusService:
    name: str
    slug: str
    origin: str
    destination: str
    operator: str
    colour: Optional[str]


def get_short_time_string(t: time) -> str:
    return time.strftime(t, "%H%M")


@dataclass
class BusTripStop:
    name: str
    atco: str
    arr_time: time
    dep_time: time

    def get_arr_time_string(self) -> str:
        return get_short_time_string(self.arr_time)

    def get_dep_time_string(self) -> str:
        return get_short_time_string(self.dep_time)


@dataclass
class BusTrip:
    id: int
    service: str
    service_slug: str
    origin: str
    destination: str
    start_time: time
    stops: List[BusTripStop]


def get_duration_string(d: timedelta) -> str:
    seconds = d.seconds
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    if hours > 0:
        hour_string = f"{hours}h"
    else:
        hour_string = ""
    return f"{hour_string}{minutes}m"


@dataclass
class BusTripSegment:
    trip: BusTrip
    board_index: int
    board: BusStop
    board_time: time
    alight_index: int
    alight: BusStop
    alight_time: time
    duration: timedelta

    def get_segment_stops(self) -> List[BusTripStop]:
        return self.trip.stops[self.board_index:self.alight_index+1]

    def get_intermediate_stops(self) -> List[BusTripStop]:
        return self.trip.stops[self.board_index+1:self.alight_index]

    def get_duration_string(self) -> str:
        return get_duration_string(self.duration)

    def get_board_time_string(self) -> str:
        return get_short_time_string(self.board_time)

    def get_alight_time_string(self) -> str:
        return get_short_time_string(self.alight_time)
