import pandas as pd

from src.db.EvedDb import EvedDb
from nicegui import ui, events


def get_vehicles() -> pd.DataFrame:
    db = EvedDb()
    return db.get_vehicles()


class MainSelector:
    def __init__(self) -> None:
        with ui.expansion(text="Vehicles", icon="directions_car").classes("w-full"):
            options = {
                "columnDefs": [
                    {"headerName": "ID", "field": "vehicle_id"},
                    {"headerName": "Type", "field": "vehicle_type"},
                    {"headerName": "Class", "field": "vehicle_class"},
                ],
                "rowSelection": "single"
            }
            self.vehicle_grid = ui.aggrid.from_pandas(get_vehicles(), options=options)
            self.vehicle_grid.on("rowSelected", lambda e: self.on_vehicle_selected(e))

        with ui.expansion(text="Trajectories", icon="route").classes("w-full"):
            ui.label("Trajectories")

        with ui.expansion(text="Geofence", icon="pentagon").classes("w-full"):
            ui.label("Geofence")

    def on_vehicle_selected(self, event: events.GenericEventArguments) -> None:
        ui.notify(event.args)