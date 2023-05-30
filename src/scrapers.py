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


def get_bus_service_url(id: int, stop_time: Optional[int] = None) -> str:
    if stop_time:
        stop_time_string = "#stop-time-{stop_time}"
    else:
        stop_time_string = ""
    return f"https://bustimes.org/trips/{id}{stop_time_string}"


def get_bus_stop_page(id: int, origin_dt: datetime) -> BeautifulSoup:
    stop_url = get_bus_stop_url(id, origin_dt)
    return get_page(stop_url)


def get_bus_stop_name(stop_page: BeautifulSoup) -> str:
    results = stop_page.find("h1")
    return results.text


def get_bus_service_page(id: int, stop_time: Optional[int] = None) -> BeautifulSoup:
    service_url = get_bus_service_url(id, stop_time=stop_time)
    print(service_url)
    return get_page(service_url)


def get_bus_number(service_page: BeautifulSoup) -> str:
    results = service_page.find("h2").text.strip().replace("\n", "")
    return results.split("-")[0]


def get_stop_details_from_service(service_page: BeautifulSoup, origin_time: int) -> Tuple[str, int, time]:
    row = service_page.find("tr", id=f"stop-time-{origin_time}")
    link = row.select_one("a")
    href = link["href"].split("/")[2]
    stop = link.text
    (hours, minutes) = row.select("td")[1].text.strip().split(":")
    time_obj = time(hour=int(hours), minute=int(minutes))
    return (href, stop, time_obj)
