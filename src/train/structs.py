from dataclasses import dataclass
from datetime import datetime
from dataclasses_json import dataclass_json

from typing import List, Optional


@dataclass_json
@dataclass
class TrainStation:
    name: str
    crs: str
    tiploc: str
    lat: Optional[float]
    lon: Optional[float]


@dataclass
class TrainStop:
    station: TrainStation
    platform: Optional[str]


@dataclass
class TrainService:
    headcode: str
    origins: List[str]
    date: datetime
