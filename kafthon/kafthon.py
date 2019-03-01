import collections
from typing import Dict, Any, Callable, Set

from .events import BaseEvent
from .runners import BaseRunner
from .utils import get_cls_path
from .hubs.base_hub import BaseHub
from .runnables import BaseRunnable
from .event_subscription import EventSubscription


class Kafthon():
    def __init__(self, event_hub: BaseHub, runner: BaseRunner, validate_events: bool = True):
        self._event_hub = event_hub
        event_hub._kafthon_app = self

        self._runner = runner
        self.validate_events = validate_events

        self._event_registry: Dict[str, BaseEvent] = {}
        self._runnable_registry: Dict[str, BaseRunnable] = {}
        self._method_sub_registry: Dict[Callable, Set[EventSubscription]] = collections.defaultdict(set)

    @property
    def event_hub(self):
        return self._event_hub

    def register(self, target: Any):
        cls_path = get_cls_path(target)
        if issubclass(target, BaseEvent):
            self._event_registry[cls_path] = target
        elif issubclass(target, BaseRunnable):
            self._runnable_registry[cls_path] = target
        else:
            raise TypeError('Can only register event and runnable classes.')

        target._kafthon_app = self

        return target

    def _register_method_subscription(self, event_type, unwrap: bool, method: Callable):
        self._method_sub_registry[method].add(
            EventSubscription(
                event_type=event_type,
                unwrap=unwrap,
                handler=method
            )
        )

    def get_event_type_by_cls_path(self, cls_path):
        return self._event_registry.get(
            cls_path
        )
