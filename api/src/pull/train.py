import xml.etree.ElementTree as ET

from dataclasses import dataclass
from typing import Optional

from credentials import Credentials

from pull.request import get_post_json, make_request
from pull.core import data_directory, download_binary, extract_gz, get_or_throw

################################################################################
#
# KnowledgeBase (KB)
#
# KnowledgeBase is a data feed published by National Rail containing static
# passenger-facing information about the # railway network. We use it for
# station and toc data.
#
################################################################################


def get_kb_url(feed: str) -> str:
    return f"https://opendata.nationalrail.co.uk/api/staticfeeds/4.0/{feed}"


def get_kb_token_url() -> str:
    return "https://opendata.nationalrail.co.uk/authenticate"


def generate_natrail_token(natrail_credentials: Credentials) -> str:
    token_url = get_kb_token_url()
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "username": natrail_credentials.user,
        "password": natrail_credentials.password,
    }
    json = get_post_json(token_url, headers=headers, data=data)
    return json["token"]


kb_stations_namespace = "http://nationalrail.co.uk/xml/station"
kb_tocs_namespace = "http://nationalrail.co.uk/xml/toc"


def prefix_namespace(namespace: str, tag: str) -> str:
    return f"{{{namespace}}}{tag}"


def get_tag_text(root: ET.Element, tag: str, namespace: Optional[str] = None) -> str:
    if namespace is not None:
        tag = prefix_namespace(namespace, tag)
    content = get_or_throw(root.find(tag))
    return get_or_throw(content.text)


def get_natrail_token_headers(natrail_token: str) -> dict:
    return {"X-Auth-Token": natrail_token}


################################################################################
#
# CORPUS
#
# CORPUS is an open data set published by Network Rail, containing translations
# between various identifiers used on the network such as CRS, TIPLOC and
# STANOX.
#
################################################################################

corpus_path = data_directory / "corpus.json"


def get_corpus_data_url() -> str:
    return "https://publicdatafeeds.networkrail.co.uk/ntrod/SupportingFileAuthenticate?type=CORPUS"


def download_corpus(corpus_credentials: Credentials):
    corpus_url = get_corpus_data_url()
    corpus_download_path = "data/corpus.gz"
    download_binary(corpus_url, corpus_download_path, credentials=corpus_credentials)
    extract_gz(corpus_download_path, corpus_path)


################################################################################
#
# BPLAN
#
# BPLAN is an open data set published by Network Rail, containing a detailed
# model of the railway network from an operational point of view.
#
################################################################################

bplan_path = data_directory / "bplan.tsv"


def get_bplan_data_url() -> str:
    return "https://wiki.openraildata.com/images/0/0e/Geography_20221210_to_20230520_from_20221211.txt.gz"


def download_bplan():
    bplan_url = get_bplan_data_url()
    bplan_download_path = "data/bplan.gz"
    download_binary(bplan_url, bplan_download_path)
    extract_gz(bplan_download_path, bplan_path)


################################################################################
# TrainStation
################################################################################


@dataclass
class TrainStation:
    name: str
    crs: str
    lat: float
    lon: float
    operator: str


def get_stations(natrail_token: str) -> list[TrainStation]:
    kb_stations_url = get_kb_url("stations")
    headers = get_natrail_token_headers(natrail_token)
    kb_stations = make_request(kb_stations_url, headers=headers).text
    kb_stations_xml = ET.fromstring(kb_stations)
    stations = []
    for stn in kb_stations_xml.findall(
        prefix_namespace(kb_stations_namespace, "Station")
    ):
        station_name = get_tag_text(stn, "Name", kb_stations_namespace)
        station_crs = get_tag_text(stn, "CrsCode", kb_stations_namespace)
        station_lat = float(get_tag_text(stn, "Latitude", kb_stations_namespace))
        station_lon = float(get_tag_text(stn, "Longitude", kb_stations_namespace))
        station_operator = get_tag_text(stn, "StationOperator", kb_stations_namespace)
        station = TrainStation(
            station_name, station_crs, station_lat, station_lon, station_operator
        )
        stations.append(station)
    return stations


################################################################################
# TOC (Train Operating Company)
################################################################################


@dataclass
class Toc:
    name: str
    atoc: str


def get_tocs(natrail_token: str) -> list[tuple[str, str]]:
    kb_tocs_url = get_kb_url("tocs")
    headers = get_natrail_token_headers(natrail_token)
    kb_tocs = make_request(kb_tocs_url, headers=headers).text
    kb_tocs_xml = ET.fromstring(kb_tocs)
    tocs = []
    for toc in kb_tocs_xml.findall(
        prefix_namespace(kb_tocs_namespace, "TrainOperatingCompany")
    ):
        toc_name = get_tag_text(toc, "Name", kb_tocs_namespace)
        toc_code = get_tag_text(toc, "AtocCode", kb_tocs_namespace)
        tocs.append((toc_name, toc_code))
    return tocs
