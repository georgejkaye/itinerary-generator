from dataclasses import dataclass
from datetime import time
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
    stop: BusStop
    time: time


@dataclass
class BusTrip:
    service: BusService
    id: int
    start_time: time
    stops: List[BusTripStop]
