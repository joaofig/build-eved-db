from nicegui import ui
from src.ui.message.Messenger import Messenger
from src.ui.selectors.MainSelector import MainSelector
from src.ui.views.MapLayerView import MapLayerView


class MainView:
    def __init__(self, messenger: Messenger):
        self.messenger = messenger

        with ui.splitter(value=20).classes("h-dvh w-dvw") as v_splitter:
            with v_splitter.after:
                MapLayerView(messenger)
            with v_splitter.before:
                MainSelector(messenger)
