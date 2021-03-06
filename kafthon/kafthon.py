import logging
import importlib
import functools
import collections
from typing import Dict, Any, Callable, Set, Optional

from .events import BaseEvent
from .runners import BaseRunner
from .utils import get_cls_path
from .hubs.base_hub import BaseHub
from .runnables import BaseRunnable
from .event_subscription import EventSubscription


logger = logging.getLogger(__name__)


class Kafthon():
    def __init__(self, event_hub: BaseHub, runner: BaseRunner, validate_events: bool = True):
        self._event_hub = event_hub
        event_hub._kafthon_app = self

        self._runner = runner
        self.validate_events = validate_events

        self._event_registry: Dict[str, BaseEvent] = {}
        self._runnable_registry: Dict[str, BaseRunnable] = {}
        self._method_sub_registry: Dict[Callable, Set[EventSubscription]] = collections.defaultdict(set)
        self._signal_handlers: Dict[str, Set[Callable]] = collections.defaultdict(set)

        self._BaseEvent: Optional[type] = None
        self._BaseRunnable: Optional[type] = None

    @property
    def event_hub(self):
        return self._event_hub

    @property
    def BaseEvent(self):
        if self._BaseEvent is None:
            self._BaseEvent = type('BaseEvent', (BaseEvent,), dict(_kafthon_app=self))
        return self._BaseEvent

    @property
    def BaseRunnable(self):
        if self._BaseRunnable is None:
            self._BaseRunnable = type('BaseRunnable', (BaseRunnable,), dict(_kafthon_app=self))
        return self._BaseRunnable

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
        if cls_path not in self._event_registry:
            module_path, _ = cls_path.split('-')
            importlib.import_module(module_path)

        return self._event_registry.get(
            cls_path
        )

    def bind_signal(self, handler: Optional[Callable] = None, signal_type: str = None):
        if signal_type is None:
            raise TypeError('signal_type argument must not be None')

        if handler is None:
            return functools.partial(self.bind_signal, signal_type=signal_type)

        self._signal_handlers[signal_type].add(handler)

    def fire_signal(self, signal_type: str, *args, **kwargs):
        handler_set = self._signal_handlers.get(signal_type)
        if handler_set:
            for handler in handler_set:
                try:
                    handler(*args, **kwargs)
                except:
                    logger.exception('Error occurred during signal handling.')
