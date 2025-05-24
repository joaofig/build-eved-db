from nicegui import ui


@ui.page("/")
async def index():
    ui.label("Test")


ui.run()
