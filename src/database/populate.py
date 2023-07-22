from credentials import get_api_credentials

from database.connection import connect, disconnect

from bus.data import download_naptan, read_naptan
from bus.structs import BusStop

from train.data import generate_natrail_token, get_stations, get_tocs
from train.structs import Toc, TrainStation


def str_or_none_to_str(x: str | None) -> str:
    if x is None or x == "":
        return "''"
    else:
        replaced = x.replace("\u2019", "'")
        return f"$${replaced}$$"


def list_of_str_and_none_to_postgres_str(values: list[str | None]) -> list[str]:
    return list(map(str_or_none_to_str, values))


def insert(cur, table: str, fields: list[str], values: list[list[str | None]]):
    partition_length = 500
    partitions = [
        values[i * partition_length : (i + 1) * partition_length]
        for i in range((len(values) + partition_length - 1) // partition_length)
    ]
    rows = ",".join(fields)
    for partition in partitions:
        value_strings = list(
            map(
                lambda x: f"({','.join(list_of_str_and_none_to_postgres_str(x))})",
                partition,
            )
        )
        statement = f"""
            INSERT into {table}({rows})
            VALUES {",".join(value_strings)}
        """
        print(statement)
        cur.execute(statement)


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
    insert(cur, "Bus_Stop", fields, values)
    conn.commit()


def populate_train_station_table(cur, conn, stations: list[TrainStation]):
    fields = ["crs", "name", "lat", "lon", "operator"]
    values: list[list[str | None]] = list(
        map(
            lambda x: [x.crs, x.name, str(x.lat), str(x.lon), x.operator],
            stations,
        )
    )
    insert(cur, "Train_Station", fields, values)
    conn.commit()


def populate_toc_table(cur, conn, tocs: list[Toc]):
    fields = ["name", "code", "fg_colour", "bg_colour"]
    values: list[list[str | None]] = list(
        map(lambda x: [x.name, x.code, x.fg_colour, x.bg_colour], tocs)
    )
    insert(cur, "Toc", fields, values)
    conn.commit()


def populate_bus_stops(cur, conn):
    download_naptan()
    stops = read_naptan()
    populate_bus_stop_table(cur, conn, stops)


def populate_train_stations(cur, conn):
    natrail_credentials = get_api_credentials("NATRAIL")
    token = generate_natrail_token(natrail_credentials)
    stations = get_stations(token)
    populate_train_station_table(cur, conn, stations)


def populate_tocs(cur, conn):
    natrail_credentials = get_api_credentials("NATRAIL")
    token = generate_natrail_token(natrail_credentials)
    tocs = get_tocs(token)
    populate_toc_table(cur, conn, tocs)


def populate_all():
    (conn, cur) = connect()
    populate_bus_stops(cur, conn)
    populate_train_stations(cur, conn)
    disconnect(conn, cur)
