from typing import Optional, Tuple
import requests
from bs4 import BeautifulSoup  # type: ignore
from datetime import datetime, time


def get_page(url: str) -> BeautifulSoup:
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")


def get_bus_stop_url(id: int, dt: datetime = datetime.now()) -> str:
    date_string = datetime.strftime(dt, "%Y-%m-%d")
    time_string = datetime.strftime(dt, "%H%%3A%M")
    return f"https://bustimes.org/stops/{id}?date={date_string}&time={time_string}"


def get_bus_trip_url(id: int, stop_time: Optional[int] = None) -> str:
    if stop_time:
        stop_time_string = "#stop-time-{stop_time}"
    else:
        stop_time_string = ""
    return f"https://bustimes.org/trips/{id}{stop_time_string}"


def get_bus_stop_page(id: int, origin_dt: datetime) -> BeautifulSoup:
    stop_url = get_bus_stop_url(id, origin_dt)
    return get_page(stop_url)


def get_bus_stop_name(stop_page: BeautifulSoup) -> str:
    results = stop_page.select_one("h1")
    return results.text


def get_bus_trip_page(id: int, stop_time: Optional[int] = None) -> BeautifulSoup:
    trip_url = get_bus_trip_url(id, stop_time=stop_time)
    return get_page(trip_url)


def get_bus_number(trip_page: BeautifulSoup) -> str:
    results = trip_page.select_one("h2").text.strip().replace("\n", "")
    return results.split("-")[0]


def get_stop_details_from_trip(trip_page: BeautifulSoup, stop_time: int) -> Tuple[str, int, time]:
    row = trip_page.select_one("tr", id=f"stop-time-{stop_time}")
    link = row.select_one("a")
    stop_id = link["href"].split("/")[2]
    stop = link.text
    (hours, minutes) = row.select("td")[1].text.strip().split(":")
    time_obj = time(hour=int(hours), minute=int(minutes))
    return (stop, stop_id, time_obj)


def get_stop_time_from_stop_id(trip_page: BeautifulSoup, stop_id: int) -> Optional[int]:
    rows = trip_page.select("tr")
    for row in rows:
        link = row.select_one("a")
        candidate_stop_id = link["href"].split("/")[2]
        if int(candidate_stop_id) == stop_id:
            return row["id"].split("-")[2]
    return None
