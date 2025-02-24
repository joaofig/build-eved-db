from nicegui import ui

from src.ui.message.Messenger import Messenger
from src.ui.models.map import MapModel
from src.ui.views.LayerView import LayerView
from src.ui.views.MapView import MapView


class MapLayerView:
    def __init__(self, messenger: Messenger):
        self.map_model = MapModel()

        with ui.splitter(value=20,
                         horizontal=True,
                         reverse=True).classes("h-dvh w-dvw") as h_splitter:
            with h_splitter.before:
                MapView(messenger, self.map_model)
            with h_splitter.after:
                LayerView(messenger, self.map_model)