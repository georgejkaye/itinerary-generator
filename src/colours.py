import os

from typing import Any, Optional

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bus.scrapers import get_bus_stop
from bus.structs import BusTrip

from data import colours_dir, record_colours


def get_service_colour(slug: str) -> Optional[tuple[str, str]]:
    service_file = colours_dir / slug
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


def get_bus_trip_colour(trip: BusTrip, driver) -> tuple[str, str]:
    possible_colour = get_service_colour(trip.slug)
    if possible_colour is not None:
        return possible_colour
    bg_colour = None
    fg_colour = None
    try:
        current_stop_index = 0
        while bg_colour is None and fg_colour is None:
            current_stop_atco = trip.stops[current_stop_index].stop.atco
            current_stop = get_bus_stop(current_stop_atco)
            search_string = f"bus stop {current_stop.name} {current_stop.indicator} {current_stop.street} {current_stop.parent}"
            search_url = f"https://www.google.co.uk/maps/?q={search_string}"
            make_selenium_request(driver, search_url)
            element = wait_for_selector(driver, 30, ".cb7kab, .cukLmd")
            if "cookies" in element.text:
                print("opened cookies")
                close_google_cookies_screen(driver)
            print("closed cookies")
            elements = driver.find_elements(By.CLASS_NAME, "Bzv5Cd")
            for elem in elements:
                if elem.text.startswith(trip.number):
                    style = elem.get_attribute("style")
                    style_dict = get_style_dict(style)
                    bg_colour = get_colour(style_dict, "background-color", "#808080")
                    fg_colour = get_colour(style_dict, "color", "#ffffff")
                    break
            current_stop_index = current_stop_index + 1
    except:
        print("Could not get colour!")
        fg_colour = input("Background colour: ")
        bg_colour = input("Foreground colour: ")
    record_colours(trip.slug, bg_colour, fg_colour)
    return (bg_colour, fg_colour)
