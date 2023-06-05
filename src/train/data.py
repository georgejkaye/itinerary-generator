from typing import List
from request import get_page, select_all, select_one
from train.structs import TrainStation
import string


def get_station_data_link_for_letter(letter: str) -> str:
    return f"http://www.railwaycodes.org.uk/stations/station{letter}.shtm"


def get_station_data_for_letter(letter: str) -> List[TrainStation]:
    url = get_station_data_link_for_letter(letter)
    data_page = get_page(url)
    rows = select_all(data_page, "tbody tr")
    stations = []
    for row in rows:
        cols = select_all(row, "td")
        status_col = cols[2]
        if not "closed" in status_col.text.lower():
            station_col = select_one(row, "td")
            name = station_col.find(text=True, recursive=False)
            try:
                crs = select_one(station_col, ".r").text[1:-1]
            except RuntimeError:
                continue
            lon_text = cols[5].text
            if lon_text == "":
                lon = None
            else:
                lon = float(lon_text.replace("\r", "\n").split("\n")[0])
            lat_text = cols[6].text
            if lat_text == "":
                lat = None
            else:
                lat = float(lat_text.replace("\r", "\n").split("\n")[0])
            station = TrainStation(name, crs, lat, lon)
            stations.append(station)
    return stations


def get_station_data() -> List[TrainStation]:
    stations = []
    for i in range(0, 26):
        letter = string.ascii_lowercase[i]
        letter_stations = get_station_data_for_letter(letter)
        stations = stations + letter_stations
    return stations
