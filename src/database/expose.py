import json
from pathlib import Path
import sys

from database.connection import connect, disconnect


def expose_toc_colours(file: Path | str, cur):
    statement = "SELECT code, fg, bg FROM Toc_Colours"
    cur.execute(statement)
    rows = cur.fetchall()
    colours_dict = {}
    for row in rows:
        colours_dict[row[0]] = {"fg": row[1], "bg": row[2]}
    with open(file, "w+") as f:
        f.write(json.dumps(colours_dict))


toc_colours_file = "toc-colours.json"


def expose_all(root: Path | str):
    (conn, cur) = connect()
    expose_toc_colours(Path(root) / toc_colours_file, cur)
    disconnect(conn, cur)


if __name__ == "__main__":
    expose_all(sys.argv[1])
