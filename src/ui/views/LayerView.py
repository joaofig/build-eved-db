from nicegui import ui
from src.ui.message.Messenger import Messenger, AppMsg
from src.ui.models.map import MapModel


class LayerView:
    def __init__(self, messenger: Messenger, map_model: MapModel) -> None:
        self.messenger = messenger
        self.map_model = map_model

        # with ui.row().classes("w-full"):
        #     ui.button("Test")

        with ui.row().classes("w-full"):
            with ui.tabs() as tabs:
                polylines = ui.tab("Polylines")
                polygons = ui.tab("Polygons")
                trips = ui.tab("Trips")
                markers = ui.tab("Markers")

            with ui.tab_panels(tabs, value=polylines).classes("w-full"):
                with ui.tab_panel(polylines):
                    ui.label("Polylines")
                with ui.tab_panel(polygons):
                    ui.label("Polygons")
                with ui.tab_panel(trips):
                    ui.label("Trips")
                with ui.tab_panel(markers):
                    ui.label("Markers")

        # messenger.subscribe("map", "add_trip", self.on_add_trip)


    def on_add_trip(self, data: AppMsg) -> None:
        pass