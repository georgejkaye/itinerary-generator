import gzip
import json
import os
import shutil
import string
from typing import List
from bs4 import Tag

from request import Credentials, get_page, make_request, select_all, select_one
from train.structs import TrainStation


def get_corpus_data_url() -> str:
    return "https://publicdatafeeds.networkrail.co.uk/ntrod/SupportingFileAuthenticate?type=CORPUS"


def download_corpus(corpus_creds: Credentials):
    corpus_url = get_corpus_data_url()
    response = make_request(corpus_url, credentials=corpus_creds, stream=True)
    if response.status_code != 200:
        raise RuntimeError("Could not get CORPUS")
    with open("data/corpus.gz", "wb") as f:
        f.write(response.raw.read())
    with gzip.open("data/corpus.gz", "rb") as f:
        with open("data/corpus.json", "wb") as out:
            shutil.copyfileobj(f, out)
    os.remove("data/corpus.gz")


def get_station_data_url_for_letter(letter: str) -> str:
    return f"http://www.railwaycodes.org.uk/stations/station{letter}.shtm"


def get_station_crs_url_for_letter(letter: str) -> str:
    return f"http://www.railwaycodes.org.uk/crs/crs{letter}.shtm"


def has_crs(tag: Tag) -> bool:
    cells = select_all("td")
    return not cells[1].has_attr("class")


def get_station_data_for_letter(letter: str) -> List[TrainStation]:
    url = get_station_data_url_for_letter(letter)
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
    stations: List[TrainStation] = []
    for i in range(0, 26):
        letter = string.ascii_lowercase[i]
        print(f"Getting stations for {letter.upper()}...")
        letter_stations = get_station_data_for_letter(letter)
        stations = stations + letter_stations
    return stations


def write_station_data(stations: List[TrainStation], file: str):
    station_json = TrainStation.schema().dumps(stations, many=True)  # type: ignore
    with open(file, "w") as f:
        f.write(station_json)


def read_station_data(file: str) -> List[TrainStation]:
    with open(file, "r") as f:
        station_json = f.read()
    return TrainStation.schema().loads(station_json, many=True)  # type: ignore


def write_crs_tiploc_translator(stations: List[TrainStation], file: str):
    crs_dict = {}
    for stn in stations:
        crs_dict[stn.crs] = stn.tiploc
    with open(file, "w") as f:
        f.write(json.dumps(crs_dict, indent=4))
