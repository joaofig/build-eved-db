from typing import Dict, List, Tuple
from nicegui import ui
from nicegui.elements.leaflet_layers import GenericLayer


class LeafletMap:
    def __init__(
        self,
        zoom: int = 3,
        classes: str = "h-full w-full",
        options: Dict | None = None,
        draw_control: Dict | None = None,
    ) -> None:
        self.map = ui.leaflet(zoom=zoom, options=options, draw_control=draw_control)

        if len(classes) > 0:
            self.map.classes(classes)

    def polyline(
        self, points: List[Tuple[float, float]], props: Dict | None = None
    ) -> GenericLayer:
        return self.map.generic_layer(name="polyline", args=[points, props])
