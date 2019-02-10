import random

from .fixture import MyEvent


def test_event_receive_wrapped():
    mock = MyEvent.get_subscribed_mock(unwrap=True)
    mock.assert_not_called()

    event = MyEvent(x=random.random(), y=random.random()).send()

    mock.assert_called_once()
    assert dict(event, z=0) == mock.call_args[1]


def test_event_receive_unwrapped():
    mock = MyEvent.get_subscribed_mock(unwrap=False)
    mock.assert_not_called()

    event = MyEvent(x=random.random(), y=random.random()).send()

    mock.assert_called_once()
    assert (dict(event, z=0),) == mock.call_args[0]
