import os

from typing import Any, Callable, Optional, TypeVar

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from data import colours_dir, record_colours

from bus.structs import BusTrip, BusTripStop
from train.structs import TrainService, TrainServiceStop


def get_service_colour(colour_directory: str, slug: str) -> Optional[tuple[str, str]]:
    service_file = colours_dir / colour_directory / slug
    if os.path.exists(service_file):
        with open(service_file, "r") as f:
            colours = f.readlines()
        return (colours[0], colours[1])
    return None


def rgb_to_hex(r: int, g: int, b: int) -> str:
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def wait_for_selector(driver, time: int, selector: str) -> Any:
    return WebDriverWait(driver, time).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, selector))
    )


def close_google_cookies_screen(driver):
    button = driver.find_element(By.XPATH, "//*[text()='Reject all']")
    if button is not None:
        button.click()
        wait_for_selector(driver, 30, ".cukLmd")


def make_selenium_request(driver, url: str):
    print(f"Making request to {url}")
    driver.get(url)


def get_colour(style_dict: dict[str, str], field: str, default: str) -> str:
    try:
        value = style_dict[field]
        rgb = value[4:-1].replace(", ", ",").split(",")
        (r, g, b) = rgb[0], rgb[1], rgb[2]
        return rgb_to_hex(int(r), int(g), int(b))
    except:
        return default


def get_style_dict(style: str) -> dict[str, str]:
    splits = style.replace("; ", ";").split(";")
    style_dict = {}
    for split in splits[:-1]:
        colon_split = split.replace(": ", ":").split(":")
        field = colon_split[0]
        value = colon_split[1]
        style_dict[field] = value
    return style_dict


def check_for_route(driver, route: str) -> Optional[Any]:
    elements = driver.find_elements(By.CLASS_NAME, "Bzv5Cd")
    for elem in elements:
        if elem.text.startswith(route):
            return elem
    return None


T = TypeVar("T")


def get_segment_colour(
    colour_directory: str,
    route: str,
    route_identifier: str,
    stops: list[T],
    get_search_string: Callable[[T], str],
    driver,
) -> tuple[str, str]:
    possible_colours = get_service_colour(colour_directory, route_identifier)
    if possible_colours is not None:
        return possible_colours
    bg_colour = None
    fg_colour = None
    try:
        current_stop_index = 0
        while bg_colour is None and fg_colour is None:
            current_stop = stops[current_stop_index]
            search_string = get_search_string(current_stop)
            search_url = f"https://www.google.co.uk/maps/?q={search_string}"
            make_selenium_request(driver, search_url)
            try:
                element = wait_for_selector(driver, 30, ".cb7kab, .cukLmd")
                if "cookies" in element.text:
                    close_google_cookies_screen(driver)
                route_box = check_for_route(driver, route)
                if route_box is not None:
                    style = route_box.get_attribute("style")
                    style_dict = get_style_dict(style)
                    bg_colour = get_colour(style_dict, "background-color", "#808080")
                    fg_colour = get_colour(style_dict, "color", "#ffffff")
                    break
            except:
                pass
            current_stop_index = current_stop_index + 1
    except:
        print("Could not get colour!")
        fg_colour = input("Background colour: ")
        bg_colour = input("Foreground colour: ")
    record_colours(colour_directory, route_identifier, bg_colour, fg_colour)
    return (bg_colour, fg_colour)


def get_bus_stop_search_string(stop: BusTripStop) -> str:
    return f"bus stop {stop.stop.name} {stop.stop.indicator} {stop.stop.street} {stop.stop.parent}"


def get_railway_station_search_string(station: TrainServiceStop) -> str:
    return f"{station.stop.get_name()} train station {station.stop.station.crs}"


def get_bus_trip_colour(trip: BusTrip, driver) -> tuple[str, str]:
    return get_segment_colour(
        "bus", trip.number, trip.slug, trip.stops, get_bus_stop_search_string, driver
    )


def get_train_trip_colour(trip: TrainService, driver) -> tuple[str, str]:
    return get_segment_colour(
        "train",
        trip.operator,
        trip.operator.lower().replace(" ", "-"),
        trip.stops,
        get_railway_station_search_string,
        driver,
    )
