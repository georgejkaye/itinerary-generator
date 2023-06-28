from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple
from arrow import Arrow
import arrow
from dataclasses_json import dataclass_json
from bus.urls import get_bus_service_url, get_bus_stop_url, get_bus_trip_url

from structs import (
    Segment,
    ServiceInterface,
    StopInterface,
    TripInterface,
    TripStopInterface,
)


@dataclass_json
@dataclass
class BusStop(StopInterface):
    name: str
    indicator: str
    bearing: str
    lat: float
    lon: float
    naptan: Optional[str]
    atco: str

    def get_name(self) -> str:
        return f"{self.name} ({self.indicator})"

    def get_url(self) -> str:
        return get_bus_stop_url(self.atco)

    def get_latlon(self) -> Tuple[float, float]:
        return (self.lat, self.lon)

    def get_location(self) -> Optional[str]:
        return self.indicator

    def get_identifiers(self):
        return {"naptan": self.naptan, "atco": self.atco}


@dataclass
class BusStopWindow:
    stop: BusStop
    time: Arrow


@dataclass
# class BusService(ServiceInterface[BusStop]):
class BusService(ServiceInterface):
    number: str
    slug: str
    origin: str
    destination: str
    operator: str
    colour: Optional[str]

    def get_identifier(self) -> str:
        return self.number

    def get_name(self) -> str:
        return f"{self.origin} - {self.destination}"

    def get_url(self) -> str:
        return get_bus_service_url(self.slug)

    def get_origins(self) -> List[str]:
        return [self.origin]

    def get_destinations(self) -> List[str]:
        return [self.destination]

    def get_operator(self) -> str:
        return self.operator

    def get_colour(self) -> Optional[str]:
        return self.colour


@dataclass
# class BusTripStop(TripStopInterface[BusStop]):
class BusTripStop(TripStopInterface):
    stop: BusStop
    arr_time: Arrow
    dep_time: Arrow

    def get_name(self) -> str:
        return self.stop.name

    def get_identifier(self) -> str:
        return self.stop.atco

    def get_location(self) -> Optional[str]:
        return self.stop.indicator

    def get_url(self) -> str:
        return get_bus_stop_url(self.stop.atco, dt=self.dep_time)

    def get_arr_time(self) -> Arrow:
        return self.arr_time

    def get_dep_time(self) -> Arrow:
        return self.dep_time


@dataclass
# class BusTrip(TripInterface[BusStop]):
class BusTrip(TripInterface):
    id: int
    number: str
    slug: str
    origin: str
    destination: str
    start_time: Arrow
    stops: List[BusTripStop]
    operator: str

    def get_identifier(self) -> str:
        return self.number

    def get_name(self) -> str:
        return f"{self.origin} - {self.destination}"

    def get_start_datetime(self) -> Arrow:
        return self.start_time

    def get_url(self) -> str:
        return get_bus_trip_url(self.id)

    def get_service_url(self) -> str:
        return get_bus_service_url(self.slug)

    def get_origins(self) -> List[str]:
        return [self.origin]

    def get_destinations(self) -> List[str]:
        return [self.destination]

    def get_stops(self) -> Sequence[BusTripStop]:
        return self.stops

    def get_operator(self) -> str:
        return self.operator
