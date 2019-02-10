from .base_hub import BaseHub
from ..events import BaseEvent


class SimpleHub(BaseHub):
    reraise_errors = True

    def send(self, event):
        if not isinstance(event, BaseEvent):
            raise TypeError('The event argument must be an instance of BaseEvent.')

        self._invoke_handlers(event)


__all__ = ['SimpleHub']
