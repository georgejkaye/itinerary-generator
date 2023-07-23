from database.connection import connect, disconnect
from database.schema import *


def create_table(cur, name: str, fields: list[str]):
    all_fields = ", ".join(fields)
    statement = f"CREATE TABLE {name} ({all_fields})"
    cur.execute(statement)


def create_bus_stop_table(cur):
    fields = [
        "atco TEXT NOT NULL PRIMARY KEY",
        "naptan TEXT",
        "name TEXT NOT NULL",
        "parent_locality TEXT",
        "locality TEXT NOT NULL",
        "landmark TEXT",
        "street TEXT",
        "indicator TEXT",
        "bearing TEXT NOT NULL",
        "lat FLOAT NOT NULL",
        "lon FLOAT NOT NULL",
    ]
    create_table(cur, bus_stop_table, fields)


def create_train_station_table(cur):
    fields = [
        "crs TEXT NOT NULL",
        "name TEXT NOT NULL",
        "lat FLOAT NOT NULL",
        "lon FLOAT NOT NULL",
        "operator TEXT NOT NULL",
    ]
    create_table(cur, train_station_table, fields)


def create_colours_table(cur):
    fields = [
        "name TEXT NOT NULL PRIMARY KEY",
        "type TEXT NOT NULL",
        "foreground TEXT NOT NULL",
        "background TEXT NOT NULL",
    ]
    create_table(cur, colours_table, fields)


def create_tocs_table(cur):
    fields = ["name TEXT NOT NULL", "atoc TEXT NOT NULL PRIMARY KEY"]
    create_table(cur, toc_table, fields)


def create_colour_table(cur):
    fields = [
        "type TEXT NOT NULL",
        "code TEXT NOT NULL",
        "fg_colour TEXT",
        "bg_colour TEXT",
    ]
    create_table(cur, colours_table, fields)


def create_brands_table(cur):
    fields = [
        "parent TEXT NOT NULL",
        "atoc TEXT NOT NULL",
        "brand TEXT NOT NULL",
        "endpoints TEXT[]",
    ]
    create_table(cur, brand_table, fields)


def create_all():
    (conn, cur) = connect()
    create_bus_stop_table(cur)
    create_train_station_table(cur)
    create_colours_table(cur)
    create_brands_table(cur)
    conn.commit()
    disconnect(conn, cur)


if __name__ == "__main__":
    create_all()
