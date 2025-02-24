from nicegui import ui, events
from src.ui.LeafletMap import LeafletMap
from src.ui.message.Messenger import Messenger, AppMsg
from src.ui.models.map import MapModel
from src.ui.models.trip import TripList
from src.ui.services.trip import get_gps_trajectory


class MapView:
    def __init__(self, messenger: Messenger, map_model: MapModel):
        self.messenger = messenger
        self.m: LeafletMap
        self.model = map_model

        options = {
            "maxZoom": 22,
        }
        draw_control = {
            "draw": {
                "polygon": True,
                "marker": False,
                "circle": False,
                "rectangle": False,
                "polyline": False,
                "circlemarker": False,
            },
            "edit": {
                "edit": True,
                "remove": True,
            },
        }


        with ui.row().classes("w-full h-full"):
            self.m = LeafletMap(
                zoom=3, draw_control=draw_control, options=options  #, classes="h-full w-full"
            )
        with ui.row():
            self.center_btn = (
                ui.button(icon="crop_free")
                .tooltip("Center map")
                # .classes("mt-0")
                .on_click(self.on_center_map_clicked)
            )
            self.clear_btn = (
                ui.button(icon="clear")
                .tooltip("Clear map")
                # .classes("mt-0")
                .on_click(self.on_clear_map_clicked)
            )

        messenger.subscribe("map", "show_trips", self.on_show_trip)

    def on_show_trip(self, msg: AppMsg) -> None:
        ui.notify(msg.data)

        trip_list: TripList = msg.data
        if trip_list.type == "gps":
            for trip_id in trip_list.trips:
                traj = get_gps_trajectory(trip_id)
                # polyline: PolylineModel = PolylineModel(traj)
                self.m.polyline(traj)

    def on_center_map_clicked(self, e: events.ClickEventArguments) -> None:
        ui.notify("Center Map!")

    def on_clear_map_clicked(self, e: events.ClickEventArguments) -> None:
        ui.notify("Clear Map!")

