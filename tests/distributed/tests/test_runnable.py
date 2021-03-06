import time
import random
import threading

import pytest

from ..kafthon_config import app, EventA, EventB, MyDockerRunnable, get_subscribed_mock


@pytest.mark.integration_test
def test_docker_runnable():
    mock = get_subscribed_mock(EventB, unwrap=False)
    container = MyDockerRunnable.deploy()
    time.sleep(1)

    try:
        threading.Thread(
            target=lambda: app.event_hub.start_receiving(timeout_ms=10000, max_records=1)
        ).start()
        mock.assert_not_called()

        random_x = random.random()
        EventA(x=random_x).send()
        time.sleep(1)

        mock.assert_called_once_with(
            dict(y=random_x ** 2)
        )
    finally:
        container.remove(force=True)

    # Event hub must be reset, because bindings otherwise remain.
    # Kafthon does not support weak references yet.
    app.event_hub.perform_reset()
