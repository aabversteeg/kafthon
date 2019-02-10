from typing import Callable

from .events import BaseEvent


class EventSubscription():
    def __init__(self, event_type: BaseEvent, unwrap: bool, handler: Callable):
        self._event_type = event_type
        self._unwrap = unwrap
        self._handler = handler

    @property
    def event_type(self):
        return self._event_type

    @property
    def unwrap(self):
        return self._unwrap

    @property
    def handler(self):
        return self._handler

    def __hash__(self):
        return hash((
            self._event_type,
            self._unwrap,
            self._handler
        ))
