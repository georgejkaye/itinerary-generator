from fastapi import FastAPI

from database.methods import connect, disconnect

from structs.bus import BusStop, BusRoute, select_bus_route, select_bus_stop
from structs.train import TocWithColours, select_toc

app = FastAPI()


@app.get("/bus/stop/{atco}", response_model=BusStop)
async def get_stop(atco: str):
    (conn, cur) = connect()
    stop = select_bus_stop(cur, atco)
    disconnect(conn, cur)
    return stop


@app.get("/bus/route/{slug}", response_model=BusRoute)
async def get_route(slug: str):
    (conn, cur) = connect()
    route = select_bus_route(cur, slug)
    disconnect(conn, cur)
    return route


@app.get("/train/toc/{atoc}", response_model=TocWithColours)
async def get_toc(atoc: str):
    (conn, cur) = connect()
    toc = select_toc(cur, atoc)
    disconnect(conn, cur)
    return toc
