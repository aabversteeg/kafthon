import time
import threading

import pytest

from ..kafthon_config import EventA, get_subscribed_mock, app
from ..kafka_runner import kafka_runner


@pytest.mark.integration_test
def test_kafka_hub():
    kafka_runner.run()
    mock = get_subscribed_mock(EventA, unwrap=True)

    threading.Thread(
        target=lambda: app.event_hub.start_receiving(timeout_ms=500, max_records=1)
    ).start()
    mock.assert_not_called()

    event = EventA(x=3).send()
    time.sleep(.1)
    mock.assert_called_once()

    mock.assert_called_once_with(**event)

    # Event hub must be reset, because bindings otherwise remain.
    # Kafthon does not support weak references yet.
    app.event_hub.perform_reset()
