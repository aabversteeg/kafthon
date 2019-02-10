from unittest.mock import MagicMock

from kafthon import Kafthon, SimpleHub, BaseEvent, Field, BaseRunnable, SimpleRunner


app = Kafthon(
    event_hub=SimpleHub(),
    runner=SimpleRunner(),
    validate_events=True
)


@app.register
class MyEvent(BaseEvent):
    x = Field(float)
    y = Field(float)
    z = Field(float, default=0)

    @classmethod
    def get_subscribed_mock(cls, unwrap):
        mock = MagicMock()
        cls.subscribe(mock, unwrap=unwrap)
        return mock


@app.register
class MySimpleRunnable(BaseRunnable):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Is used to check whether the runnable processed an event.
        self.process_event_mock = MagicMock()

    @MyEvent.subscribe
    def process_event(self, **kwargs):
        self.process_event_mock(**kwargs)


@app.register
class ResponseEvent(BaseEvent):
    pass


@app.register
class MyDockerRunnable(BaseRunnable):
    @MyEvent.subscribe
    def process_event(self, **kwargs):
        ResponseEvent().send()
