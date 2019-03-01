import os
import sys

from kafthon.registry import registry
from .serializers import MsgpackSerializer

try:
    import typeguard # NOQA
except ImportError:
    import subprocess
    subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])


def start_runnable(runnable_path, init_data=None):
    if init_data:
        init_args, init_kwargs = MsgpackSerializer.deserialize(init_data)
    else:
        init_args, init_kwargs = (), {}

    runnable_cls = registry.get_runnable(runnable_path)
    runnable = runnable_cls(*init_args, **init_kwargs)
    runnable._kafthon_app.event_hub.start_receiving()


if __name__ == '__main__':
    start_runnable(
        sys.argv[1],
        os.environ.get('KAFTHON_INIT_DATA')
    )
