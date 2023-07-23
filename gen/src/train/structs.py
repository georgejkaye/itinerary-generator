from dataclasses import dataclass
from arrow import Arrow
from typing import Dict, List, Optional, Sequence, Tuple

from structs import StopInterface, TripInterface, TripStopInterface

from train.urls import get_train_service_url, get_train_station_url


@dataclass
class Brand:
    atoc: str
    endpoints: list[str]


@dataclass
class Toc:
    name: str
    code: str
    fg_colour: str
    bg_colour: str


@dataclass
class TrainStation:
    name: str
    crs: str
    lat: float
    lon: float
    operator: Toc


@dataclass
class TrainStop(StopInterface):
    station: TrainStation
    platform: Optional[str]

    def get_name(self) -> str:
        return f"{self.station.name}"

    def get_url(self) -> str:
        return get_train_station_url(self.station.crs)

    def get_latlon(self) -> Tuple[Optional[float], Optional[float]]:
        return (self.station.lat, self.station.lon)

    def get_location(self) -> Optional[str]:
        return self.platform

    def get_identifiers(self) -> Dict[str, Optional[str]]:
        return {"crs": self.station.crs}


@dataclass
class TrainServiceStop(TripStopInterface):
    stop: TrainStop
    arrival: Optional[Arrow]
    departure: Optional[Arrow]

    def get_name(self) -> str:
        return self.stop.get_name()

    def get_identifier(self) -> str:
        return self.stop.station.crs

    def get_location(self) -> Optional[str]:
        return self.stop.get_location()

    def get_url(self) -> str:
        return get_train_station_url(self.stop.station.crs, datetime=self.departure)

    def get_arr_time(self) -> Optional[Arrow]:
        return self.arrival

    def get_dep_time(self) -> Optional[Arrow]:
        return self.departure


@dataclass
class TrainService(TripInterface):
    id: str
    headcode: str
    run_datetime: Arrow
    origins: List[TrainStation]
    destinations: List[TrainStation]
    stops: List[TrainServiceStop]
    operator: Toc

    def get_identifier(self) -> str:
        return self.headcode

    def get_name(self) -> str:
        origin_string = "&".join(self.get_origins())
        destination_string = "&".join(self.get_destinations())
        start_time_string = self.run_datetime.format("HHmm")
        return f"{start_time_string} {origin_string} to {destination_string}"

    def get_url(self) -> str:
        return get_train_service_url(self.id, self.run_datetime)

    def get_service_url(self) -> str:
        return get_train_service_url(self.id, self.run_datetime)

    def get_origins(self) -> List[str]:
        return list(map(lambda x: x.name, self.origins))

    def get_start_datetime(self) -> Arrow:
        return self.run_datetime

    def get_destinations(self) -> List[str]:
        return list(map(lambda x: x.name, self.destinations))

    def get_stops(self) -> Sequence[TrainServiceStop]:
        return self.stops

    def get_operator(self) -> str:
        return self.operator.name

    def get_colour(self) -> Optional[str]:
        return None
