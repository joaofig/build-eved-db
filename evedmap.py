from nicegui import ui, events

from src.ui.message.Messenger import Messenger
from src.ui.LeafletMap import LeafletMap
from src.ui.views.MainView import MainView


@ui.page("/")
async def index():
    ui.query(".nicegui-content").classes("py-0 px-0")
    ui.page_title("eVED Viewer")

    messenger = Messenger()

    MainView(messenger)


ui.run()
