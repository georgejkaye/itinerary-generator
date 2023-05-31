from dataclasses import dataclass
from datetime import time, timedelta
from typing import List, Optional


@dataclass
class BusStop:
    name: str
    stand: Optional[str]
    lat: float
    lon: float
    naptan: str
    atco: int


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


@dataclass
class BusTripStop:
    name: str
    atco: int
    time: time


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
    minutes = int(seconds / 60)
    if hours > 0:
        hour_string = f"{hours}h"
    else:
        hour_string = ""
    return f"{hour_string}{minutes}m"


@dataclass
class BusTripSegment:
    trip: BusTrip
    board: int
    alight: int
    duration: timedelta

    def get_segment_stops(self) -> List[BusTripStop]:
        return self.trip.stops[self.board:self.alight+1]

    def get_boarding_stop(self) -> BusTripStop:
        return self.trip.stops[self.board]

    def get_alighting_stop(self) -> BusTripStop:
        return self.trip.stops[self.alight]
