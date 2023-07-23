from http.client import HTTPException
from typing import Optional
from fastapi import FastAPI, HTTPException

from database.methods import connect, disconnect

from structs.bus import BusStop, BusRoute, select_bus_route, select_bus_stop
from structs.train import (
    TocData,
    TrainStation,
    TrainStationData,
    select_toc,
    select_train_station,
)

app = FastAPI()


@app.get("/bus/stop/{atco}", response_model=BusStop)
async def get_stop(atco: str):
    (conn, cur) = connect()
    stop = select_bus_stop(cur, atco)
    disconnect(conn, cur)
    if stop is None:
        raise HTTPException(status_code=404, detail=f"Atco {atco} not found")
    return stop


@app.get("/bus/route/{slug}", response_model=BusRoute)
async def get_route(slug: str):
    (conn, cur) = connect()
    route = select_bus_route(cur, slug)
    disconnect(conn, cur)
    if route is None:
        raise HTTPException(status_code=404, detail=f"Slug {slug} not found")
    return route


@app.get("/train/station/{descriptor}", response_model=TrainStationData)
async def get_station(descriptor: str):
    (conn, cur) = connect()
    station = select_train_station(cur, descriptor)
    disconnect(conn, cur)
    if station is None:
        raise HTTPException(
            status_code=404, detail=f"Station with descriptor {descriptor} not found"
        )
    return station


@app.get("/train/toc/{atoc}", response_model=TocData)
async def get_toc(atoc: str):
    (conn, cur) = connect()
    toc = select_toc(cur, atoc)
    disconnect(conn, cur)
    if toc is None:
        raise HTTPException(status_code=404, detail=f"Toc with atoc {atoc} not found")
    return toc
