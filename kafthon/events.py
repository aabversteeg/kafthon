from __future__ import annotations

import operator
import functools
from typing import Optional, Callable

from . import kafthon
from .field import Field, NOT_SET
from .utils import check_is_method
from .exceptions import ValidationError
from .field_mapping import FieldMapping
from .signals import ON_EVENT_SENT


class MetaEvent(type):
    def __new__(cls, cls_name, base_cls, attributes, **kwargs):
        if cls_name != 'BaseEvent':
            field_mapping = {}
            for attr, value in list(attributes.items()):
                if isinstance(value, Field):
                    del attributes[attr]
                    field_mapping[attr] = value
            attributes['_fields'] = FieldMapping(field_mapping)

        event_cls = super().__new__(cls, cls_name, base_cls, attributes, **kwargs)

        kafthon_app = getattr(event_cls, '_kafthon_app', None)
        if kafthon_app is not None:
            kafthon_app.register(event_cls)

        return event_cls


class BaseEvent(dict, metaclass=MetaEvent):
    _kafthon_app: kafthon.Kafthon
    _fields: FieldMapping = FieldMapping({})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__set_defaults()

    def __set_defaults(self):
        missing = self._fields.all_field_names - set(self.keys())
        for field_name in missing:
            default = self._fields[field_name].get_default()
            if default != NOT_SET:
                self[field_name] = default

    @classmethod
    def subscribe(cls, handler: Optional[Callable] = None, unwrap: bool = True):
        if handler is None:
            return functools.partial(cls.subscribe, unwrap=unwrap)

        if check_is_method(handler):
            cls._kafthon_app._register_method_subscription(
                event_type=cls,
                unwrap=unwrap,
                method=handler
            )
            return handler

        cls._subscribe(handler, unwrap)

    @classmethod
    def _subscribe(cls, handler, unwrap):
        return cls._kafthon_app.event_hub.subscribe(
            cls,
            handler,
            unwrap=unwrap
        )

    def send(self):
        __tracebackhide__ = operator.methodcaller("errisinstance", ValidationError)

        self._kafthon_app.fire_signal(ON_EVENT_SENT, event=self)

        if self._kafthon_app.validate_events:
            self.validate()

        self._kafthon_app.event_hub.send(self)
        return self

    def validate(self):
        __tracebackhide__ = operator.methodcaller("errisinstance", ValidationError)
        self._fields.validate_event(self)

    def __repr__(self):
        return '<%s %s>' % (
            type(self).__name__,
            super().__repr__()
        )
    __str__ = __repr__
