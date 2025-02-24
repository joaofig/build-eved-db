from dataclasses import dataclass
from typing import List


@dataclass
class TripList:
    trips: List[int]
    type: str  # gps, match, mode
