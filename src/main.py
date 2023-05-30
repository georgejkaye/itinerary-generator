import yaml
from scrapers import get_bus_number, get_bus_trip_page, get_stop_details_from_trip

with open("examples/test.yml", "r") as data:
    text = yaml.safe_load(data)

for journey in text["journeys"]:
    for leg in journey["legs"]:
        if leg["type"] == "bus":
            id = leg["id"]
            origin = leg["origin"]
            destination = leg["destination"]
            trip_page = get_bus_trip_page(leg["id"])
            print(get_bus_number(trip_page))
            print(get_stop_details_from_trip(trip_page, origin))
            print(get_stop_details_from_trip(trip_page, destination))
