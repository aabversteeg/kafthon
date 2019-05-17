from __future__ import annotations

import logging
import collections
from typing import Dict, Callable, Set

from .. import kafthon
from ..events import BaseEvent
from ..event_subscription import EventSubscription
from ..signals import ON_EVENT_RECEIVE


logger = logging.getLogger(__name__)


class BaseHub():
    _kafthon_app: kafthon.Kafthon
    reraise_errors = False

    def __init__(self, reraise_errors=False):
        self.reraise_errors = reraise_errors
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
        self._kafthon_app.fire_signal(ON_EVENT_RECEIVE, event=event)

        event_type = type(event)
        event_subs = self._subscriptions.get(event_type) or ()

        for sub in event_subs:
            try:
                if sub.unwrap:
                    sub.handler(**event)
                else:
                    sub.handler(event)
            except Exception as error:
                if self.reraise_errors:
                    raise error
                else:
                    logger.exception('An event handler raised an exception')

    def send(self, event):
        raise NotImplementedError()

    def start_receiving(self, event):
        raise NotImplementedError()

    def perform_reset(self):
        self._subscriptions.clear()

    def has_subscriptions(self):
        return bool(self._subscriptions)


__all__ = ['BaseHub']
