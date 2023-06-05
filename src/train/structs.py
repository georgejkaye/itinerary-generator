from dataclasses import dataclass

from typing import Optional


@dataclass
class TrainStation:
    name: str
    crs: str
    lat: Optional[float]
    lon: Optional[float]


@dataclass
class TrainStop:
    station: TrainStation
    platform: Optional[str]
