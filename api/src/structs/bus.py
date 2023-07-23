from dataclasses import dataclass
from typing import Optional

from database.methods import select
from database.schema import bus_stop_table, colour_table


@dataclass
class BusStop:
    atco: str
    naptan: Optional[str]
    name: str
    locality: str
    parent: str
    landmark: Optional[str]
    street: str
    indicator: Optional[str]
    bearing: Optional[str]
    lat: float
    lon: float


def select_bus_stop(cur, atco: str) -> BusStop:
    rows = select(
        cur,
        [
            "atco",
            "naptan",
            "name",
            "parent_locality",
            "locality",
            "landmark",
            "street",
            "indicator",
            "bearing",
            "lat",
            "lon",
        ],
        bus_stop_table,
        ["atco = %(atco)s"],
        {"atco": atco},
    )
    if len(rows) != 1:
        raise RuntimeError(f"No match for atco {atco}")
    else:
        row = rows[0]
        return BusStop(
            row[0],
            row[1],
            row[2],
            row[3],
            row[4],
            row[5],
            row[6],
            row[7],
            row[8],
            row[9],
            row[10],
        )


@dataclass
class BusRoute:
    fg: str
    bg: str


def select_bus_route(cur, slug: str) -> BusRoute:
    rows = select(
        cur,
        ["fg", "bg"],
        colour_table,
        ["type=%(type)s", "code=%(slug)s"],
        {"type": "bus", "slug": slug},
    )
    if len(rows) != 1:
        raise RuntimeError(f"No match for slug {slug}")
    else:
        row = rows[0]
        return BusRoute(row[0], row[1])
