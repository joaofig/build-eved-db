from nicegui import ui, events
from nicegui.events import ValueChangeEventArguments
from nicegui.elements.leaflet import Leaflet
from src.ui.MainSelector import MainSelector


def on_map_draw(e: events.GenericEventArguments) -> None:
    # layer_type = e.args['layerType']
    # print(f"Draw {layer_type}")
    print(e.args)


def create_map() -> Leaflet:
    options = {
        "maxZoom": 22,
    }
    draw_control = {
        'draw': {
            'polygon': True,
            'marker': False,
            'circle': False,
            'rectangle': False,
            'polyline': False,
            'circlemarker': False,
        },
        'edit': {
            'edit': True,
            'remove': True,
        },
    }
    m = (ui.leaflet(zoom=3,
                    draw_control=draw_control,
                    options=options)
         .classes("h-full w-full"))
    m.on('draw:created', on_map_draw)
    return m


@ui.page('/')
async def index():
    ui.query('.nicegui-content').classes('py-0 px-0')
    ui.page_title("eVED Viewer")

    m = None
    with ui.splitter(value=20).classes("h-dvh w-dvw") as splitter:
        with splitter.after:
            m = create_map()
        with splitter.before:
            main_selector = MainSelector()


ui.run()
