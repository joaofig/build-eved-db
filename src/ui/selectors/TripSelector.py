from typing import List

import pandas as pd

from nicegui import ui, events
from src.db.EvedDb import EvedDb
from src.ui.message.Messenger import Messenger, AppMsg
from src.ui.models.trip import TripList


def get_trips() -> pd.DataFrame:
    db = EvedDb()
    return db.get_trajectories()


class TripSelector:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger
        self.selected_trips = set()

        with ui.column().classes("w-full items-start"):
            options = {
                "columnDefs": [
                    {
                        "headerName": "ID",
                        "field": "traj_id",
                        "filter": True,
                        "headerCheckboxSelection": True,
                        "checkboxSelection": True,
                    },
                    {"headerName": "Vehicle", "field": "vehicle_id", "filter": True},
                    {"headerName": "Trip", "field": "trip_id", "filter": True},
                ],
                "rowSelection": "multiple",
                "headerCheckbox": True,
            }
            self.trips_df = get_trips()
            self.grid = ui.aggrid.from_pandas(self.trips_df, options=options)
            self.grid.on("rowSelected", self.on_row_selected)

            with ui.row():
                self.gps_btn = (
                    ui.button(icon="location_disabled")
                    .tooltip("Show noisy GPS trip locations")
                    .on_click(self.show_noisy_gps_trips_clicked)
                )
                self.match_btn = (
                    ui.button(icon="my_location")
                    .tooltip("Show map-matched trip locations")
                    .on_click(self.show_map_matched_trips_clicked)
                    # .on_click(self.on_clear_clicked)
                )
                self.node_btn = (
                    ui.button(icon="polyline")
                    .tooltip("Show map-matched trip nodes")
                )

        messenger.subscribe("vehicle", "filter", self.on_filter_vehicles)

    def on_center_map_clicked(self, _: events.ClickEventArguments) -> None:
        self.messenger.send("map", AppMsg("center_map"))

    def on_clear_clicked(self, event: events.ClickEventArguments) -> None:
        pass

    def filter_grid(self, vehicles: List[int]):
        if len(vehicles) == 0:
            df = self.trips_df
        else:
            df = self.trips_df[self.trips_df["vehicle_id"].isin(vehicles)]
        rows = df.to_dict(orient="records")
        self.grid.run_grid_method("setGridOption", "rowData", rows)

    def on_filter_vehicles(self, msg: AppMsg) -> None:
        self.filter_grid(msg.data)

    def on_row_selected(self, event: events.GenericEventArguments) -> None:
        selected = event.args["selected"]
        trip_id = event.args["data"]["trip_id"]

        if selected:
            self.selected_trips.add(trip_id)
        else:
            self.selected_trips.remove(trip_id)

    def show_noisy_gps_trips_clicked(self, _: events.ClickEventArguments) -> None:
        self.messenger.send(
            "map", AppMsg("show_trips", TripList(list(self.selected_trips), "gps"))
        )

    def show_map_matched_trips_clicked(self, _: events.ClickEventArguments) -> None:
        self.messenger.send(
            "map", AppMsg("show_trips", TripList(list(self.selected_trips), "match"))
        )

    def show_map_node_trips_clicked(self, _: events.ClickEventArguments) -> None:
        self.messenger.send(
            "map", AppMsg("show_trips", TripList(list(self.selected_trips), "node"))
        )
