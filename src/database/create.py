from database.connection import connect, disconnect


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
    create_table(cur, "Bus_Stop", fields)


def create_train_station_table(cur):
    fields = [
        "tiploc TEXT NOT NULL PRIMARY KEY",
        "crs TEXT NOT NULL",
        "name TEXT NOT NULL",
        "lat FLOAT",
        "lon FLOAT",
    ]
    create_table(cur, "Train_Station", fields)


def create_colours_table(cur):
    fields = [
        "name TEXT NOT NULL PRIMARY KEY",
        "type TEXT NOT NULL",
        "foreground TEXT NOT NULL",
        "background TEXT NOT NULL",
    ]
    create_table(cur, "Colour", fields)


def create_brands_table(cur):
    fields = [
        "parent_company TEXT NOT NULL",
        "brand TEXT NOT NULL",
        "unique_endpoints TEXT[]",
    ]
    create_table(cur, "Brands", fields)


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
