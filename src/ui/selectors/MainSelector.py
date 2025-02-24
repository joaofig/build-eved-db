from nicegui import ui

from src.ui.message.Messenger import Messenger
from src.ui.selectors.TripSelector import TripSelector
from src.ui.selectors.VehicleSelector import VehicleSelector


class MainSelector:
    def __init__(self, messenger: Messenger) -> None:
        self.messenger = messenger

        with ui.expansion(text="Vehicles", icon="directions_car").classes("w-full"):
            vehicles = VehicleSelector(messenger)

        with ui.expansion(text="Trips", icon="route").classes("w-full"):
            trips = TripSelector(messenger)

        with ui.expansion(text="Geofence", icon="pentagon").classes("w-full"):
            ui.label("Geofence")

        with ui.expansion(text="Settings", icon="settings").classes("w-full"):
            ui.label("Settings")
