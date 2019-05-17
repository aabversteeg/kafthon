import os
import sys

from kafthon.registry import registry
from .serializers import MsgpackSerializer


def start_runnable(runnable_path, init_kwargs=None):
    if init_kwargs:
        init_kwargs = MsgpackSerializer.deserialize(init_kwargs)
    else:
        init_kwargs = {}

    runnable_cls = registry.get_runnable(runnable_path)
    runnable = runnable_cls(**init_kwargs)
    runnable._kafthon_app.event_hub.start_receiving()


if __name__ == '__main__':
    start_runnable(
        sys.argv[1],
        os.environ.get('KAFTHON_INIT_KWARGS')
    )
