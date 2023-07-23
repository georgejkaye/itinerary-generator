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
