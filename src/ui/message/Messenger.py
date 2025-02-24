from typing import Callable, Any


class AppMsg:
    def __init__(self, name: str, data: Any | None = None):
        self.name = name
        self.data = data
        self.result = None  # How to use this?

    @classmethod
    def make(cls, name: str, data: Any | None = None) -> "AppMsg":
        return cls(name, data)


class Messenger:
    def __init__(self):
        self.channels = dict()

    def send(self, channel: str, message: AppMsg):
        if channel in self.channels.keys():
            if message.name in self.channels[channel]:
                for handler in self.channels[channel][message.name]:
                    handler(message)

    def subscribe(self, channel: str, name: str, handler: Callable[[AppMsg], None]):
        if channel not in self.channels:
            self.channels[channel] = {name: [handler]}
        else:
            self.channels[channel][name].append(handler)
