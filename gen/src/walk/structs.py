from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple
from arrow import Arrow

from walk.urls import get_osm_map_at_latlon_url, get_walking_instructions_url

from structs import (
    StopInterface,
    TripInterface,
    TripStopInterface,
)


@dataclass
class WalkPoint(StopInterface):
    name: str
    lat: float
    lon: float

    def get_name(self) -> str:
        return f"{self.name}"

    def get_url(self) -> str:
        return get_osm_map_at_latlon_url(self.lat, self.lon, 18)

    def get_latlon(self) -> Tuple[Optional[float], Optional[float]]:
        return (self.lat, self.lon)

    def get_location(self) -> Optional[str]:
        return None

    def get_identifiers(self) -> dict[str, Optional[str]]:
        return {}


@dataclass
# class BusTripStop(TripStopInterface[BusStop]):
class WalkStop(TripStopInterface):
    stop: WalkPoint
    time: Arrow

    def get_name(self) -> str:
        return self.stop.name

    def get_identifier(self) -> str:
        return f"@{self.stop.lat}, {self.stop.lon}"

    def get_location(self) -> Optional[str]:
        return None

    def get_url(self) -> str:
        return self.stop.get_url()

    def get_arr_time(self) -> Arrow:
        return self.time

    def get_dep_time(self) -> Arrow:
        return self.time


@dataclass
# class WalkTrip(TripInterface[WalkStop]):
class WalkTrip(TripInterface):
    origin: WalkStop
    destination: WalkStop
    duration: float
    distance: float

    def get_identifier(self) -> str:
        return "Walk"

    def get_name(self) -> str:
        return f"{self.origin.get_name()} - {self.destination.get_name()}"

    def get_start_datetime(self) -> Arrow:
        return self.origin.get_dep_time()

    def get_url(self) -> Optional[str]:
        return get_walking_instructions_url(
            self.origin.stop.lat,
            self.origin.stop.lon,
            self.destination.stop.lat,
            self.destination.stop.lon,
        )

    def get_service_url(self) -> Optional[str]:
        return None

    def get_origins(self) -> List[str]:
        return [self.origin.get_name()]

    def get_destinations(self) -> List[str]:
        return [self.destination.get_name()]

    def get_stops(self) -> Sequence[WalkStop]:
        return [self.origin, self.destination]

    def get_operator(self) -> Optional[str]:
        return None
