from typing import Tuple
from arrow import Arrow
from bs4 import BeautifulSoup
from dotenv import dotenv_values
import openrouteservice
from request import select_one


def get_direction_stats(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> Tuple[float, float]:
    key = dotenv_values().get("ORS_KEY")
    client = openrouteservice.Client(key=key)
    routes = client.directions(((lon1, lat1), (lon2, lat2)), profile="foot-walking")
    summary = routes["routes"][0]["summary"]
    distance = summary["distance"]
    duration = summary["duration"]
    return (distance, duration)
