
from typing import List, Tuple
from pydantic import BaseModel, Field


class LayerModel(BaseModel):
    visible: bool = True
    color: str = "blue"
    opacity: float = 1.0


class MarkerModel(LayerModel):
    icon_anchor: Tuple[int, int] = (0, 0)
    lat: float = 0.0
    lng: float = 0.0
    popup: str = ""
    icon: str = ""
    size: int = 10


class PolylineModel(LayerModel):
    points: List[Tuple[float, float]] = Field(default_factory=list)
    color: str = "blue"


class TripModel(PolylineModel):
    traj_id: int = 0
    color: str = "green"


class PolygonModel(LayerModel):
    points: List[Tuple[float, float]] = Field(default_factory=list)
    color: str = "gray"


class MapModel(BaseModel):
    markers: List[MarkerModel] = list()
    polylines: List[PolylineModel] = list()
    polygons: List[PolygonModel] = list()
    trips_gps: List[TripModel] = list()
    trips_match: List[TripModel] = list()
    trips_node: List[TripModel] = list()

    def add_trip(self, trip: TripModel) -> None:
        pass
