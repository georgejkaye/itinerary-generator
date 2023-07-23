from credentials import Credentials

from pull.core import (
    data_directory,
    download_binary,
    extract_gz,
    get_or_throw,
    get_post_json,
)

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
