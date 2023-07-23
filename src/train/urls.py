from typing import Optional
from arrow import Arrow


def get_train_service_url(id: str, date: Arrow) -> str:
    date_string = date.format("YYYY-MM-DD")
    return f"https://www.realtimetrains.co.uk/service/gb-nr:{id}/{date_string}/detailed"


def get_train_station_url(crs: str, datetime: Optional[Arrow] = None) -> str:
    if datetime is None:
        date_string = ""
    else:
        date_string = f"/{datetime.format('YYYY-MM-DD')}/{datetime.format('HHmm')}"
    return f"https://www.realtimetrains.co.uk/search/detailed/gb-nr:{crs}{date_string}"
