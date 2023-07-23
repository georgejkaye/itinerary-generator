from credentials import get_api_credentials

from database.methods import connect, disconnect, insert
from database.schema import *

from pull.bus import BusStop, download_naptan, read_naptan
from pull.train import generate_natrail_token
from structs.train import Toc, TrainStation, pull_stations, pull_tocs


def populate_bus_stop_table(cur, conn, stops: list[BusStop]):
    fields = [
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
    ]
    values: list[list[str | None]] = list(
        map(
            lambda x: [
                x.atco,
                x.naptan,
                x.name,
                x.parent,
                x.locality,
                x.landmark,
                x.street,
                x.indicator,
                x.bearing,
                str(x.lat),
                str(x.lon),
            ],
            stops,
        )
    )
    insert(cur, bus_stop_table, fields, values)
    conn.commit()


def populate_train_station_table(cur, conn, stations: list[TrainStation]):
    fields = ["crs", "name", "lat", "lon", "operator"]
    values: list[list[str | None]] = list(
        map(
            lambda x: [x.crs, x.name, str(x.lat), str(x.lon), x.operator],
            stations,
        )
    )
    insert(cur, train_station_table, fields, values)
    conn.commit()


def populate_toc_table(cur, conn, tocs: list[Toc]):
    fields = ["name", "atoc"]
    values: list[list[str | None]] = list(map(lambda x: [x.name, x.atoc], tocs))
    insert(cur, toc_table, fields, values)
    conn.commit()


def populate_bus_stops(cur, conn):
    download_naptan()
    stops = read_naptan()
    populate_bus_stop_table(cur, conn, stops)


def populate_train_stations(cur, conn):
    natrail_credentials = get_api_credentials("NATRAIL")
    token = generate_natrail_token(natrail_credentials)
    stations = pull_stations(token)
    populate_train_station_table(cur, conn, stations)


def populate_tocs(cur, conn):
    natrail_credentials = get_api_credentials("NATRAIL")
    token = generate_natrail_token(natrail_credentials)
    tocs = pull_tocs(token)
    populate_toc_table(cur, conn, tocs)


def populate_all():
    (conn, cur) = connect()
    populate_bus_stops(cur, conn)
    populate_train_stations(cur, conn)
    disconnect(conn, cur)
