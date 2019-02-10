from __future__ import annotations

from . import kafthon


class BaseRunnable():
    _kafthon_app: kafthon.Kafthon

    def __init__(self):
        for attr in self.__class__.__dict__.values():
            if attr in self._kafthon_app._method_sub_registry:
                unbound_method = attr
                for subscription in self._kafthon_app._method_sub_registry[unbound_method]:
                    bound_method = getattr(self, unbound_method.__name__)
                    subscription.event_type._subscribe(
                        bound_method,
                        unwrap=subscription.unwrap
                    )

    @classmethod
    def deploy(cls, *args, **kwargs):
        return cls._kafthon_app._runner.run(
            cls,
            init_data=(args, kwargs)
        )
