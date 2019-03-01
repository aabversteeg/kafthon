from ..kafthon_config import MyEvent, MyLocalRunnable


def test_local_runnable():
    runnable = MyLocalRunnable.deploy()
    runnable.process_event_mock.assert_not_called()

    event = MyEvent(x=0, y=0).send()
    assert event == runnable.process_event_mock.call_args[1]
