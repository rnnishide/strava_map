from enum import Enum

from pydantic.dataclasses import dataclass


class ActivityTypes(Enum):
    CYCLING = "cycling"
    RUN = "running"


@dataclass
class Activity:
    coordinates: tuple[tuple[float, float], ...]
    elevation: tuple[float, ...]
    start_time: str
    name: str
    type: ActivityTypes
