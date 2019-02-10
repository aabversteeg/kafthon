from kafthon import DockerContainerRunner
from .fixture import app, MyEvent, MySimpleRunnable, MyDockerRunnable


def test_simple_runnable():
    runnable = MySimpleRunnable.deploy()
    runnable.process_event_mock.assert_not_called()

    event = MyEvent(x=0, y=0).send()
    assert event == runnable.process_event_mock.call_args[1]


def test_docker_runnable(monkeypatch):
    runner = DockerContainerRunner(
        docker_kwargs=dict(image='python')
    )
    monkeypatch.setattr(app, '_runner', runner)
    MyDockerRunnable.deploy()
