import re
from typing import List, Optional, Tuple
from bs4 import BeautifulSoup, Tag
from arrow import Arrow
import arrow

from bus.structs import BusStop, BusTrip, BusTripStop
from bus.urls import get_bus_service_url, get_bus_stop_url, get_bus_trip_url
from request import get_href, get_id, get_page, select_all, select_one


def get_bus_stop_page(atco: str, origin_dt: Arrow) -> BeautifulSoup:
    stop_url = get_bus_stop_url(atco, origin_dt)
    return get_page(stop_url)


def get_bus_stop_name(stop_page: BeautifulSoup) -> str:
    result = select_one(stop_page, "h1")
    return result.text


def get_bus_stop_latlon(stop_page: BeautifulSoup) -> Tuple[float, float]:
    result = select_one(stop_page, ".horizontal a")
    href = get_href(result)
    split = href.split("/")
    try:
        lat = split[2]
        lon = split[3]
    except:
        raise RuntimeError(f"Could not find latitude and longitude in link {href}")
    return (float(lat), float(lon))


def get_bus_stop_naptan(stop_page: BeautifulSoup) -> Optional[str]:
    try:
        result = select_one(stop_page, '[title="NaPTAN code"]')
    except RuntimeError:
        return None
    return result.text


def get_bus_stop_atco(stop_page: BeautifulSoup) -> str:
    result = select_one(stop_page, '[title="ATCO code"]')
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
    result = select_one(trip_page, "h2")
    return result.text.strip().replace("\n", "").split("-")[0]


def get_trip_origin_and_destination(trip_page: BeautifulSoup) -> Tuple[str, str]:
    result = select_one(trip_page, "h2")
    result_text = result.text.replace("\n", "")
    first_hyphen = result_text.replace("\n", "").find("-")
    route = result_text[first_hyphen + 1 :]
    route_split = route.split(" to ")
    origin = route_split[0]
    destination = route_split[1]
    return (origin, destination)


def get_bus_service_page(slug: str) -> BeautifulSoup:
    service_url = get_bus_service_url(slug)
    return get_page(service_url)


def get_full_stop_name_from_service_page(service_page: BeautifulSoup, atco: str) -> str:
    a = select_one(service_page, f'a[href*="{atco}"]')
    return a.text


def get_bus_service_number_and_slug(trip_page: BeautifulSoup) -> Tuple[str, str]:
    result = select_one(trip_page, "ol li:nth-child(3) a")
    href = get_href(result)
    slug = href.split("/")[2]
    number = slug.split("-")[0]
    return (number, slug)


def get_time_from_trip_stop_row(date: Arrow, row: Tag, cell_index: int) -> Arrow:
    time_text = (
        select_all(row, "td")[cell_index].contents[0].text.replace("\n", "").strip()
    )
    (hours, minutes) = time_text.split(":")
    return arrow.get(date.year, date.month, date.day, int(hours), int(minutes), 0)


def get_trip_stop_details(
    date: Arrow, arr_row: Tag, dep_row: Optional[Tag], service_page: BeautifulSoup
) -> BusTripStop:
    link = select_one(arr_row, "a")
    href = get_href(link)
    atco = href.split("/")[2]
    full_stop_name = get_full_stop_name_from_service_page(service_page, atco)
    stop_matches = re.match(bracket_regex, full_stop_name)
    if stop_matches is None:
        stop_name = full_stop_name
        stop_location = None
    else:
        stop_name = stop_matches.group(1)
        stop_location = stop_matches.group(2)
    arr_time = get_time_from_trip_stop_row(date, arr_row, 1)
    if dep_row is None:
        dep_time = arr_time
    else:
        dep_time = get_time_from_trip_stop_row(date, dep_row, 0)
    return BusTripStop(stop_name, stop_location, atco, arr_time, dep_time)


def get_trip_stop_details_at_time(
    trip_page: BeautifulSoup, date: Arrow, stop_time: int, service_page: BeautifulSoup
) -> BusTripStop:
    rows = select_all(trip_page, ".trip-timetable tbody tr")
    desired_id = f"stop-time-{stop_time}"
    for i, row in enumerate(rows):
        if row["id"] == desired_id:
            td = select_one(row, "td")
            if td["rowspan"] == 2:
                arr_row = row
                dep_row = rows[i + 1]
            else:
                arr_row = row
                dep_row = None
    return get_trip_stop_details(
        date=date, arr_row=arr_row, dep_row=dep_row, service_page=service_page
    )


def get_all_trip_stop_details(
    date: Arrow, trip_page: BeautifulSoup, service_page: BeautifulSoup
) -> List[BusTripStop]:
    rows = select_all(trip_page, ".trip-timetable tbody tr")
    stop_rows = []
    current_index = 0
    while current_index < len(rows):
        arr_row = rows[current_index]
        td = select_one(arr_row, "td")
        if td.attrs.get("rowspan") is not None and td.attrs["rowspan"] == "2":
            dep_row = rows[current_index + 1]
            current_index = current_index + 2
        else:
            dep_row = None
            current_index = current_index + 1
        stop_rows.append((arr_row, dep_row))
    return list(
        map(lambda r: get_trip_stop_details(date, r[0], r[1], service_page), stop_rows)
    )


def get_stop_time_from_stop_id(trip_page: BeautifulSoup, stop_id: int) -> Optional[int]:
    rows = select_all(trip_page, "tr")
    for row in rows:
        link = select_one(row, "a")
        candidate_stop_id = get_href(link).split("/")[2]
        if int(candidate_stop_id) == stop_id:
            return int(get_id(row).split("-")[2])
    return None


def get_operator(trip_page: BeautifulSoup) -> str:
    breadcrumbs = select_all(select_one(trip_page, "ol"), "li")
    return select_one(breadcrumbs[1], "span").text


def get_bus_trip(date: Arrow, id: int) -> BusTrip:
    page = get_bus_trip_page(id)
    (trip_number, trip_slug) = get_bus_service_number_and_slug(page)
    (origin, destination) = get_trip_origin_and_destination(page)
    service_page = get_page(get_bus_service_url(trip_slug))
    stops = get_all_trip_stop_details(date, page, service_page)
    operator = get_operator(page)
    return BusTrip(
        id,
        trip_number,
        trip_slug,
        origin,
        destination,
        stops[0].dep_time,
        stops,
        operator,
    )
