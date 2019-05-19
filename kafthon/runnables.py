from __future__ import annotations
import collections

from . import kafthon
from .registry import registry


class MetaRunnable(type):
    def __new__(cls, *args, **kwargs):
        event_cls = super().__new__(cls, *args, **kwargs)
        registry.register_runnable(event_cls)
        return event_cls


class BaseRunnable(metaclass=MetaRunnable):
    _kafthon_app: kafthon.Kafthon

    def __init__(self):
        for attr in self.__class__.__dict__.values():
            if not isinstance(attr, collections.abc.Hashable):
                continue

            if attr in self._kafthon_app._method_sub_registry:
                unbound_method = attr
                for subscription in self._kafthon_app._method_sub_registry[unbound_method]:
                    bound_method = getattr(self, unbound_method.__name__)
                    subscription.event_type._subscribe(
                        bound_method,
                        unwrap=subscription.unwrap
                    )

    @classmethod
    def deploy(cls, init_kwargs=None, **kwargs):
        return cls._kafthon_app._runner.run(
            cls,
            init_kwargs=init_kwargs or {},
            **kwargs
        )
