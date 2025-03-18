"""Data types and convenient aliases."""

from enum import Enum
from typing import Tuple
from pydantic.dataclasses import dataclass

GPSCoordinate = Tuple[float, float]


class ActivityTypes(Enum):
    CYCLING = "cycling"
    RUN = "running"
    UNKNOWN = "unknown"


@dataclass
class Activity:
    coordinates: tuple[tuple[float, float], ...]
    elevation: tuple[float, ...]
    start_time: str
    name: str
    type: ActivityTypes

    class Config:
        frozen = True
