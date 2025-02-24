import pandas as pd

from nicegui import ui, events
from src.db.EvedDb import EvedDb
from src.ui.message.Messenger import Messenger, AppMsg


def get_vehicles() -> pd.DataFrame:
    db = EvedDb()
    return db.get_vehicles()


class VehicleSelector:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger
        self.selected_vehicles = set()

        with ui.column().classes("w-full items-start"):
            options = {
                "columnDefs": [
                    {
                        "headerName": "ID",
                        "field": "vehicle_id",
                        "filter": True,
                        "sortable": True,
                        "checkboxSelection": True,
                        "headerCheckboxSelection": True,
                    },
                    {
                        "headerName": "Type",
                        "field": "vehicle_type",
                        "filter": True,
                        "sortable": True,
                    },
                    {
                        "headerName": "Class",
                        "field": "vehicle_class",
                        "filter": True,
                        "sortable": True,
                    },
                ],
                "rowSelection": "multiple",
                "headerCheckbox": True,
            }
            self.grid = ui.aggrid.from_pandas(get_vehicles(), options=options).classes(
                "mb-0"
            )
            self.grid.on("rowSelected", self.on_row_selected)

            with ui.row():
                ui.button(icon="filter_alt").tooltip("Filter").on_click(
                    self.on_filter_click
                )
                ui.button(icon="filter_alt_off").tooltip("Remove filter").on_click(
                    self.on_filter_off_click
                )

    def on_filter_click(self, _: events.ClickEventArguments) -> None:
        self.messenger.send("vehicle", AppMsg("filter", list(self.selected_vehicles)))

    def on_filter_off_click(self, _: events.ClickEventArguments) -> None:
        self.messenger.send("vehicle", AppMsg("filter", []))

    def on_row_selected(self, event: events.GenericEventArguments) -> None:
        selected = event.args["selected"]
        vehicle_id = event.args["data"]["vehicle_id"]

        if selected:
            self.selected_vehicles.add(vehicle_id)
        else:
            self.selected_vehicles.remove(vehicle_id)
