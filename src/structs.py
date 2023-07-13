from abc import abstractmethod
from dataclasses import dataclass
from datetime import timedelta
from typing import Dict, List, Optional, Sequence, Tuple
from arrow import Arrow


class StopInterface:
    """Interface for a stop: a place a service may stop at"""

    @abstractmethod
    def get_name(self) -> str:
        """The name of this stop"""
        pass

    @abstractmethod
    def get_url(self) -> str:
        """Get the url of an appropriate page for this stop"""

    @abstractmethod
    def get_latlon(self) -> Tuple[Optional[float], Optional[float]]:
        pass

    def get_lat(self) -> Optional[float]:
        return self.get_latlon()[0]

    def get_lon(self) -> Optional[float]:
        return self.get_latlon()[1]

    @abstractmethod
    def get_location(self) -> Optional[str]:
        """Get the (optional) name of this platform"""
        pass

    @abstractmethod
    def get_identifiers(self) -> Dict[str, Optional[str]]:
        """All the identifiers this stop has"""
        pass

    def get_identifier(self, key: str) -> Optional[str]:
        return self.get_identifiers().get(key)


# class ServiceInterface[T]:
class ServiceInterface:
    """Interface for a service that calls at stops of type T"""

    @abstractmethod
    def get_identifier(self) -> Optional[str]:
        """Get the short identifier of this service, such as the service number"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """Get the full name of this service"""
        pass

    @abstractmethod
    def get_url(self) -> str:
        pass

    @abstractmethod
    def get_origins(self) -> List[str]:
        pass

    @abstractmethod
    def get_destinations(self) -> List[str]:
        pass

    @abstractmethod
    def get_operator(self) -> str:
        pass

    @abstractmethod
    def get_colour(self) -> Optional[str]:
        pass


# class TripStopInterface[T]:
class TripStopInterface:
    """Interface for a stop at a given time"""

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_identifier(self) -> str:
        pass

    @abstractmethod
    def get_location(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_url(self) -> str:
        pass

    @abstractmethod
    def get_arr_time(self) -> Optional[Arrow]:
        pass

    def get_arr_time_string(self) -> Optional[str]:
        arr_time = self.get_arr_time()
        if arr_time is None:
            return None
        return arr_time.format("HH:mm")

    @abstractmethod
    def get_dep_time(self) -> Optional[Arrow]:
        pass

    def get_dep_time_string(self) -> Optional[str]:
        dep_time = self.get_dep_time()
        if dep_time is None:
            return None
        return dep_time.format("HH:mm")


# class TripStopInterface[T]:
class TripInterface:
    """Interface for a trip: a specific instance of a service"""

    @abstractmethod
    def get_identifier(self) -> str:
        """Get the short identifier of this service, such as a number"""
        pass

    @abstractmethod
    def get_name(self) -> str:
        """The full name of this service"""
        pass

    def get_full_name(self) -> str:
        return f"{self.get_identifier()} - {self.get_name()}"

    @abstractmethod
    def get_start_datetime(self) -> Arrow:
        """Get the datetime that this service started at"""
        pass

    @abstractmethod
    def get_url(self) -> Optional[str]:
        """Get the url of an appropriate page about this trip"""
        pass

    @abstractmethod
    def get_service_url(self) -> Optional[str]:
        pass

    @abstractmethod
    def get_origins(self) -> List[str]:
        """Get a list of strings of origins of this trip"""
        pass

    def get_origin_string(self) -> str:
        return "&".join(self.get_destinations())

    @abstractmethod
    def get_destinations(self) -> List[str]:
        """Get a list of strings of destinations of this trip"""
        pass

    def get_destination_string(self) -> str:
        return "&".join(self.get_destinations())

    @abstractmethod
    # def get_stops(self) -> List[TripStopInterface[T]]:
    def get_stops(self) -> Sequence[TripStopInterface]:
        """Get a list of stops this trip makes"""
        pass

    @abstractmethod
    def get_operator(self) -> Optional[str]:
        """Get the name of the operator of this service"""
        pass


@dataclass
# class Segment[T]:
class Segment:
    # trip: TripInterface[T]
    trip: TripInterface
    board_index: int
    alight_index: int
    fg_colour: str
    bg_colour: str
    border_colour: str

    # def get_segment_stops(self) -> Sequence[TripStopInterface[T]]:
    def get_segment_stops(self) -> Sequence[TripStopInterface]:
        return self.trip.get_stops()[self.board_index : self.alight_index + 1]

    # def get_board_stop(self) -> TripStopInterface[T]:
    def get_board_stop(self) -> TripStopInterface:
        return self.get_segment_stops()[0]

    def get_board_time(self) -> Arrow:
        dep_time = self.get_board_stop().get_dep_time()
        if dep_time is None:
            raise RuntimeError("Never boarded service")
        return dep_time

    def get_board_time_string(self) -> str:
        return get_short_time_string(self.get_board_time())

    # def get_intermediate_stops(self) -> Sequence[TripStopInterface[T]]:
    def get_intermediate_stops(self) -> Sequence[TripStopInterface]:
        return self.get_segment_stops()[1:-1]

    # def get_alight_stop(self) -> TripStopInterface[T]:
    def get_alight_stop(self) -> TripStopInterface:
        return self.get_segment_stops()[-1]

    def get_alight_time(self) -> Arrow:
        arr_time = self.get_alight_stop().get_arr_time()
        if arr_time is None:
            raise RuntimeError("Never alighted service")
        return arr_time

    def get_alight_time_string(self) -> str:
        return get_short_time_string(self.get_alight_time())

    def get_duration(self) -> timedelta:
        board_dep = self.get_board_stop().get_dep_time()
        alight_arr = self.get_alight_stop().get_arr_time()
        # mypy can't tell that arrow overloads subtraction
        return alight_arr - board_dep  # type: ignore

    def get_duration_string(self) -> str:
        return get_duration_string(self.get_duration())

    def get_fg_colour(self) -> str:
        return f"{ self.fg_colour }"

    def get_bg_colour(self) -> str:
        return f"{ self.bg_colour }"

    def get_border_colour(self) -> Optional[str]:
        return f"{ self.border_colour }"


def get_segment(
    trip: TripInterface,
    board: str,
    alight: str,
    fg_colour: str = "#ffffff",
    bg_colour: str = "#000000",
    border_colour: str = "#000000",
) -> Optional[Segment]:
    start = None
    end = None
    for i, stop in enumerate(trip.get_stops()):
        if stop.get_identifier() == str(board):
            start = i
        elif stop.get_identifier() == str(alight):
            if start is None:
                return None
            end = i
            return Segment(trip, start, end, fg_colour, bg_colour, border_colour)
    return None


def get_short_time_string(t: Arrow) -> str:
    return t.format("HHmm")


def get_duration_string(d: timedelta) -> str:
    seconds = d.seconds
    hours = int(seconds / 3600)
    minutes = int((seconds % 3600) / 60)
    if hours > 0:
        hour_string = f"{hours}h"
    else:
        hour_string = ""
    return f"{hour_string}{minutes}m"
