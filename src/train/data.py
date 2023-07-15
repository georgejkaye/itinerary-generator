import csv
from dataclasses import dataclass
import json
import math
import os
from pathlib import Path
from convertbng.util import convert_lonlat  # type: ignore
from typing import Dict, List, Tuple, Optional
from bs4 import Tag
from credentials import get_api_credentials
from data import download_binary, extract_gz, data_directory, write_lookup

from request import Credentials, get_page, make_request, select_all, select_one
from train.structs import TrainStation

corpus_path = data_directory / "corpus.json"
bplan_path = data_directory / "bplan.tsv"
tiploc_to_crs_path = data_directory / "tiploc-to-crs.json"
crs_to_tiploc_path = data_directory / "crs-to-tiploc.json"
station_json_path = data_directory / "train-stations.json"
tiploc_lookup_path = data_directory / "tiploc-lookup.json"
crs_lookup_path = data_directory / "crs-lookup.json"


def get_bplan_data_url() -> str:
    return "https://wiki.openraildata.com/images/0/0e/Geography_20221210_to_20230520_from_20221211.txt.gz"


def get_corpus_data_url() -> str:
    return "https://publicdatafeeds.networkrail.co.uk/ntrod/SupportingFileAuthenticate?type=CORPUS"


def download_corpus(corpus_credentials: Credentials):
    corpus_url = get_corpus_data_url()
    corpus_download_path = "data/corpus.gz"
    download_binary(corpus_url, corpus_download_path, credentials=corpus_credentials)
    extract_gz(corpus_download_path, corpus_path)


def download_bplan():
    bplan_url = get_bplan_data_url()
    bplan_download_path = "data/bplan.gz"
    download_binary(bplan_url, bplan_download_path)
    extract_gz(bplan_download_path, bplan_path)


def translate_corpus_to_translators(
    corpus: dict,
) -> Tuple[Dict[str, str], Dict[str, str]]:
    stns = corpus["TIPLOCDATA"]
    tiploc_to_crs = {}
    crs_to_tiploc = {}
    for stn in stns:
        tiploc = stn["TIPLOC"]
        crs = stn["3ALPHA"]
        if not (tiploc == " " or crs == " "):
            tiploc_to_crs[tiploc] = crs
            crs_to_tiploc[crs] = tiploc
    return (tiploc_to_crs, crs_to_tiploc)


def translate_bplan_to_stations(
    bplan: list, tiploc_to_crs: Dict[str, str]
) -> List[TrainStation]:
    stations = []
    found_locs = False
    for row in bplan:
        if row[0] == "LOC":
            found_locs = True
            tiploc = row[2]
            crs = tiploc_to_crs.get(tiploc)
            if crs is not None:
                name = row[3]
                east = int(row[6])
                north = int(row[7])
                if not (east == 0 or north == 0):
                    (lons, lats) = convert_lonlat([east], [north])
                    (lon, lat) = (lons[0], lats[0])
                    if math.isnan(lon):
                        lon = None
                    if math.isnan(lat):
                        lat = None
                else:
                    (lon, lat) = (None, None)
                station = TrainStation(name, crs, tiploc, lat, lon)
                stations.append(station)
        elif found_locs:
            break
    return stations


def write_dict_as_json(data: dict, path: str | Path):
    data_json = json.dumps(data)
    with open(path, "w") as f:
        f.write(data_json)


def read_json_as_dict(path: str | Path) -> dict:
    with open(path, "r") as f:
        data = f.read()
    return json.loads(data)


def read_tsv_as_list(path: str | Path) -> list:
    rows = []
    with open(path, "r", encoding="ASCII", errors="ignore") as f:
        data = csv.reader(f, delimiter="\t")
        for row in data:
            rows.append(row)
    return rows


def has_crs(tag: Tag) -> bool:
    cells = select_all(tag, "td")
    return not cells[1].has_attr("class")


def write_station_data(stations: List[TrainStation], file: str | Path):
    station_json = TrainStation.schema().dumps(stations, many=True)  # type: ignore
    with open(file, "w") as f:
        f.write(station_json)


def read_station_data(file: str | Path) -> List[TrainStation]:
    with open(file, "r") as f:
        station_json = f.read()
    return TrainStation.schema().loads(station_json, many=True)  # type: ignore


def get_station_lookups(
    stations: List[TrainStation],
) -> Tuple[Dict[str, TrainStation], Dict[str, TrainStation]]:
    tiploc_lookup = {}
    crs_lookup = {}
    for stn in stations:
        tiploc_lookup[stn.tiploc] = stn
        crs_lookup[stn.crs] = stn
    return (tiploc_lookup, crs_lookup)


def read_station_lookup(file: str | Path) -> Dict[str, TrainStation]:
    with open(file, "r") as f:
        data = json.loads(f.read())
    station_dict = {}
    for key in data:
        station_dict[key] = TrainStation.from_dict(data[key])  # type: ignore
    return station_dict


def read_tiploc_crs_translator() -> Dict[str, str]:
    return read_json_as_dict(tiploc_to_crs_path)


def read_crs_tiploc_translator() -> Dict[str, str]:
    return read_json_as_dict(crs_to_tiploc_path)


@dataclass
class TrainData:
    tiploc_lookup: Dict[str, TrainStation]
    crs_lookup: Dict[str, TrainStation]


def setup_train_data() -> TrainData:
    if not os.path.isdir(data_directory):
        os.makedirs(data_directory)
    if not os.path.isfile(corpus_path):
        download_corpus(get_api_credentials("NR"))

    if not os.path.isfile(bplan_path):
        download_bplan()

    corpus = read_json_as_dict(corpus_path)
    (tiploc_to_crs, crs_to_tiploc) = translate_corpus_to_translators(corpus)
    write_dict_as_json(tiploc_to_crs, tiploc_to_crs_path)
    write_dict_as_json(crs_to_tiploc, crs_to_tiploc_path)
    bplan = read_tsv_as_list(bplan_path)
    stations = translate_bplan_to_stations(bplan, tiploc_to_crs)
    (tiploc_lookup, crs_lookup) = get_station_lookups(stations)
    write_lookup(tiploc_lookup, tiploc_lookup_path)
    write_lookup(crs_lookup, crs_lookup_path)
    write_station_data(stations, station_json_path)
    return TrainData(tiploc_lookup, crs_lookup)


def read_train_data() -> TrainData:
    # stations = read_station_data(station_json_path)
    tiploc_lookup = read_station_lookup(tiploc_lookup_path)
    crs_lookup = read_station_lookup(crs_lookup_path)
    return TrainData(tiploc_lookup, crs_lookup)
