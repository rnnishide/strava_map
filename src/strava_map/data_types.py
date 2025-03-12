from pydantic.dataclasses import dataclass
import datetime
from enum import Enum


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
