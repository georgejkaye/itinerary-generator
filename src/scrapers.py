import re
from typing import List, Optional, Tuple
import requests
from bs4 import BeautifulSoup, Tag  # type: ignore
from datetime import date, datetime, time

from structs import BusStop, BusTrip, BusTripSegment, BusTripStop


def get_page(url: str) -> BeautifulSoup:
    page = requests.get(url)
    return BeautifulSoup(page.content, "html.parser")


def get_bus_stop_url(atco: str, dt: datetime = datetime.now()) -> str:
    date_string = datetime.strftime(dt, "%Y-%m-%d")
    time_string = datetime.strftime(dt, "%H%%3A%M")
    return f"https://bustimes.org/stops/{atco}?date={date_string}&time={time_string}"


def get_bus_trip_url(id: int, stop_time: Optional[int] = None) -> str:
    if stop_time:
        stop_time_string = "#stop-time-{stop_time}"
    else:
        stop_time_string = ""
    return f"https://bustimes.org/trips/{id}{stop_time_string}"


def get_bus_stop_page(atco: str, origin_dt: datetime) -> BeautifulSoup:
    stop_url = get_bus_stop_url(atco, origin_dt)
    return get_page(stop_url)


def get_bus_stop_name(stop_page: BeautifulSoup) -> str:
    result = stop_page.select_one("h1")
    return result.text


def get_bus_stop_latlon(stop_page: BeautifulSoup) -> Tuple[float, float]:
    result = stop_page.select_one(".horizontal a")
    link = result["href"]
    split = link.split("/")
    lat = split[2]
    lon = split[3]
    return (float(lat), float(lon))


def get_bus_stop_naptan(stop_page: BeautifulSoup) -> Optional[str]:
    result = stop_page.select_one("[title=\"NaPTAN code\"]")
    if result is None:
        return None
    return result.text


def get_bus_stop_atco(stop_page: BeautifulSoup) -> str:
    result = stop_page.select_one("[title=\"ATCO code\"]")
    return result.text


bracket_regex = r"(.*) \((.*)\)"


def get_bus_stop(atco: str) -> BusStop:
    stop_url = get_bus_stop_url(atco)
    page = get_page(stop_url)
    stop_name = get_bus_stop_name(page)
    bracket_matches = re.match(bracket_regex, stop_name)
    if bracket_matches is not None:
        stop_name = bracket_matches.group(1)
        stop_stand = bracket_matches.group(2)
    else:
        stop_stand = None
    (stop_lat, stop_lon) = get_bus_stop_latlon(page)
    stop_naptan = get_bus_stop_naptan(page)
    stop_atco = get_bus_stop_atco(page)
    return BusStop(stop_name, stop_stand, stop_lat, stop_lon, stop_naptan, stop_atco)


def get_bus_trip_page(id: int, stop_time: Optional[int] = None) -> BeautifulSoup:
    trip_url = get_bus_trip_url(id, stop_time=stop_time)
    return get_page(trip_url)


def get_bus_number(trip_page: BeautifulSoup) -> str:
    result = trip_page.select_one("h2").text.strip().replace("\n", "")
    return result.split("-")[0]


def get_trip_origin_and_destination(trip_page: BeautifulSoup) -> Tuple[str, str]:
    result = trip_page.select_one("h2").text.replace("\n", "")
    first_hyphen = result.find("-")
    route = result[first_hyphen+1:]
    route_split = route.split(" to ")
    origin = route_split[0]
    destination = route_split[1]
    return (origin, destination)


def get_bus_service_number_and_slug(trip_page: BeautifulSoup) -> Tuple[str, str]:
    result = trip_page.select_one("ol li:nth-child(3) a")
    slug = result["href"].split("/")[2]
    number = slug.split("-")[0]
    return (number, slug)


def get_time_from_trip_stop_row(row: Tag, cell_index: int) -> time:
    time_text = row.select(
        "td")[cell_index].contents[0].replace("\n", "").strip()
    (hours, minutes) = time_text.split(":")
    return time(hour=int(hours), minute=int(minutes))


def get_trip_stop_details(arr_row: Tag, dep_row: Optional[Tag]) -> BusTripStop:
    link = arr_row.select_one("a")
    stop_id = link["href"].split("/")[2]
    stop_name = link.text
    arr_time = get_time_from_trip_stop_row(arr_row, 1)
    if dep_row is None:
        dep_time = arr_time
    else:
        dep_time = get_time_from_trip_stop_row(dep_row, 0)
    return BusTripStop(stop_name, stop_id, arr_time, dep_time)


def get_trip_stop_details_at_time(trip_page: BeautifulSoup, stop_time: int) -> BusTripStop:
    rows = trip_page.select(".trip-timetable tbody tr")
    desired_id = f"stop-time-{stop_time}"
    for (i, row) in enumerate(rows):
        if row["id"] == desired_id:
            td = row.select_one("td")
            if td["rowspan"] == 2:
                arr_row = row
                dep_row = rows[i+1]
            else:
                arr_row = row
                dep_row = None
    return get_trip_stop_details(arr_row=arr_row, dep_row=dep_row)


def get_all_trip_stop_details(trip_page: BeautifulSoup) -> List[BusTripStop]:
    rows = trip_page.select(".trip-timetable tbody tr")
    stop_rows = []
    current_index = 0
    while current_index < len(rows):
        arr_row = rows[current_index]
        td = arr_row.select_one("td")
        if td.attrs.get("rowspan") is not None and td.attrs["rowspan"] == '2':
            dep_row = rows[current_index + 1]
            current_index = current_index + 2
        else:
            dep_row = None
            current_index = current_index + 1
        stop_rows.append((arr_row, dep_row))
    return list(map(lambda r: get_trip_stop_details(r[0], r[1]), stop_rows))


def get_stop_time_from_stop_id(trip_page: BeautifulSoup, stop_id: int) -> Optional[int]:
    rows = trip_page.select("tr")
    for row in rows:
        link = row.select_one("a")
        candidate_stop_id = link["href"].split("/")[2]
        if int(candidate_stop_id) == stop_id:
            return row["id"].split("-")[2]
    return None


def get_bus_trip(id: int) -> BusTrip:
    page = get_bus_trip_page(id)
    (trip_number, trip_slug) = get_bus_service_number_and_slug(page)
    (origin, destination) = get_trip_origin_and_destination(page)
    stops = get_all_trip_stop_details(page)
    return BusTrip(id, trip_number, trip_slug, origin, destination, stops[0].dep_time, stops)


def get_bus_trip_segment(trip: BusTrip, board: str, alight: str) -> Optional[BusTripSegment]:
    start = None
    end = None
    for (i, stop) in enumerate(trip.stops):
        if stop.atco == str(board):
            start = i
        elif stop.atco == str(alight):
            if start is None:
                return None
            end = i
            start_time = trip.stops[start].dep_time
            end_time = trip.stops[end].arr_time
            duration = datetime.combine(
                date.min, end_time) - datetime.combine(date.min, start_time)
            board_stop = get_bus_stop(trip.stops[start].atco)
            alight_stop = get_bus_stop(trip.stops[end].atco)
            return BusTripSegment(trip, start, board_stop, start_time, end, alight_stop, end_time, duration)
    return None
