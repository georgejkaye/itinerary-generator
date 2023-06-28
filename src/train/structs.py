from dataclasses import dataclass
from arrow import Arrow
from dataclasses_json import dataclass_json

from typing import Dict, List, Optional, Sequence, Tuple

from structs import StopInterface, TripInterface, TripStopInterface
from train.urls import get_train_service_url, get_train_station_url


@dataclass_json
@dataclass
class TrainStation:
    name: str
    crs: str
    tiploc: str
    lat: Optional[float]
    lon: Optional[float]


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
        return {"crs": self.station.crs, "tiploc": self.station.tiploc}


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
    origins: List[str]
    destinations: List[str]
    datetime: Arrow
    stops: List[TrainServiceStop]
    operator: str

    def get_identifier(self) -> str:
        return self.headcode

    def get_name(self) -> str:
        origin_string = "&".join(self.origins)
        destination_string = "&".join(self.destinations)
        start_time_string = self.datetime.format("HHmm")
        return f"{start_time_string} {origin_string} to {destination_string}"

    def get_url(self) -> str:
        return get_train_service_url(self.id, self.datetime)

    def get_service_url(self) -> str:
        return get_train_service_url(self.id, self.datetime)

    def get_origins(self) -> List[str]:
        return self.origins

    def get_start_datetime(self) -> Arrow:
        return self.datetime

    def get_destinations(self) -> List[str]:
        return self.destinations

    def get_stops(self) -> Sequence[TrainServiceStop]:
        return self.stops

    def get_operator(self) -> str:
        return self.operator

    def get_colour(self) -> Optional[str]:
        return None
