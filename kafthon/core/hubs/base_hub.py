import logging
import collections
from typing import Dict, Callable, Set

from ..events import BaseEvent
from ..event_subscription import EventSubscription


logger = logging.getLogger(__name__)


class BaseHub():
    reraise_errors = False

    def __init__(self):
        self._subscriptions: Dict[BaseEvent, Set[EventSubscription]] = collections.defaultdict(set)

    def subscribe(self, event_type: BaseEvent, handler: Callable, unwrap: bool) -> EventSubscription:
        subscription = EventSubscription(
            event_type=event_type,
            unwrap=unwrap,
            handler=handler
        )
        self._subscriptions[event_type].add(subscription)
        return subscription

    def _invoke_handlers(self, event):
        event_type = type(event)
        event_subs = self._subscriptions.get(event_type)
        for sub in event_subs:
            try:
                if sub.unwrap:
                    sub.handler(**event)
                else:
                    sub.handler(event)
            except Exception:
                logger.exception('An event handler raised an exception')

    def send(self, event):
        raise NotImplementedError()

    def perform_reset(self):
        self._listeners.clear()


__all__ = ['BaseHub']
