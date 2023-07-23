from dotenv import dotenv_values
from psycopg2 import connect as db_connect


def connect() -> tuple:
    env = dotenv_values(".env")
    conn = db_connect(
        dbname=env["DB_NAME"],
        user=env["DB_USER"],
        password=env["DB_PASSWD"],
        host=env["DB_HOST"],
    )
    cur = conn.cursor()
    return (conn, cur)


def disconnect(conn, cur):
    conn.close()
    cur.close()


def create(cur, name: str, fields: list[str]):
    all_fields = ", ".join(fields)
    statement = f"CREATE TABLE {name} ({all_fields})"
    cur.execute(statement)


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


def select_query(cur, query: str, params: dict = {}) -> list:
    cur.execute(query, params)
    rows = cur.fetchall()
    return rows


def select(
    cur, fields: list[str], table: str, where: list[str] = [], params: dict = {}
) -> list:
    field_list = ", ".join(fields)
    statement = f"SELECT {field_list} FROM {table}"
    if len(where) > 0:
        where_list = " AND ".join(where)
        statement = f"{statement} WHERE {where_list}"
    print(statement)
    cur.execute(statement, params)
    rows = cur.fetchall()
    return rows
