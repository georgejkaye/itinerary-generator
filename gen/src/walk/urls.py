def get_osm_map_at_latlon_url(lat: float, lon: float, zoom: float) -> str:
    return (
        f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map={zoom}/{lat}/{lon}"
    )


def get_walking_instructions_url(
    lat1: float, lon1: float, lat2: float, lon2: float
) -> str:
    return f"https://www.openstreetmap.org/directions?engine=graphhopper_foot&route={lat1}%2C{lon1}%3B{lat2}%2C{lon2}"
