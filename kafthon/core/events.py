from __future__ import annotations

import re
import functools
from typing import Optional, Callable

from . import kafthon
from .field_mapping import FieldMapping
from .field import Field, NOT_SET


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

        # registry.register_event_type(event_cls)
        return event_cls


class BaseEvent(dict, metaclass=MetaEvent):
    _kafthon_app: kafthon.Kafthon
    _fields: FieldMapping = FieldMapping({})

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__set_defaults()

    def __set_defaults(self):
        missing = self._fields.field_names - set(self.keys())
        for field_name in missing:
            default = self._fields[field_name].get_default()
            if default != NOT_SET:
                self[field_name] = default

    @classmethod
    def subscribe(cls, handler: Optional[Callable] = None, unwrap: bool = True):
        if handler is None:
            return functools.partial(cls.subscribe, unwrap=unwrap)

        is_method = (
            hasattr(handler, '__code__') and
            handler.__code__.co_varnames and
            handler.__code__.co_varnames[0] == 'self'
        )

        if is_method:
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

    @classmethod
    def get_slug(cls):
        return re.sub(
            '[^a-zA-Z0-9]+',
            '_',
            f'{cls.__module__}_{cls.__qualname__}',
        )

    def send(self):
        if self._kafthon_app.validate_events:
            self.validate()

        self._kafthon_app.event_hub.send(self)
        return self

    def validate(self):
        self._fields.validate_event(self)

    @property
    def name(self):
        return type(self).__name__

    def __repr__(self):
        return '<%s %s>' % (
            self.name,
            super().__repr__()
        )
    __str__ = __repr__
