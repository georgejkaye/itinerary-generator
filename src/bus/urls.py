from typing import Optional
from arrow import Arrow
import arrow


def get_bus_stop_url(atco: str, dt: Arrow = arrow.now("Europe/London")) -> str:
    date_string = dt.format("YYYY-MM-DD")
    time_string = dt.format("HH%3Amm")
    return f"https://bustimes.org/stops/{atco}?date={date_string}&time={time_string}"


def get_bus_trip_url(id: int, stop_time: Optional[int] = None) -> str:
    if stop_time:
        stop_time_string = "#stop-time-{stop_time}"
    else:
        stop_time_string = ""
    return f"https://bustimes.org/trips/{id}{stop_time_string}"


def get_bus_service_url(slug: str) -> str:
    return f"https://bustimes.org/services/{slug}"
