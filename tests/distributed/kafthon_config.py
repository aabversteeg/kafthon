import os
from unittest.mock import Mock

import docker
import requests

from kafthon import Kafthon, KafkaHub, BaseEvent, Field, BaseRunnable, DockerContainerRunner


DOCKER_IMAGE_TAG = 'kafthon-unittest'


cwd = os.getcwd()
app = Kafthon(
    event_hub=KafkaHub(
        bootstrap_servers=['localhost:9092']
    ),
    runner=DockerContainerRunner(
        docker_kwargs=dict(
            image=DOCKER_IMAGE_TAG,
            network='host',
            volumes=[f'{cwd}:{cwd}'],
            working_dir=cwd,
            environment=dict(
                INSIDE_CONTAINER='true'
            )
        )
    ),
    validate_events=True
)


try:
    docker_client = docker.from_env()
    try:
        docker_client.images.get(DOCKER_IMAGE_TAG)
    except docker.errors.ImageNotFound:
        docker_client.images.build(
            path='./',
            dockerfile='./tests/distributed/Dockerfile',
            tag=DOCKER_IMAGE_TAG
        )
except requests.exceptions.ConnectionError:
    pass


def get_subscribed_mock(event_type, unwrap):
    mock = Mock(
        spec=lambda *a, **k: None
    )
    event_type.subscribe(mock, unwrap=unwrap)
    return mock


@app.register
class EventA(BaseEvent):
    x = Field(float)


@app.register
class EventB(BaseEvent):
    y = Field(float)


@app.register
class MyDockerRunnable(BaseRunnable):
    @EventA.subscribe
    def process_event(self, x):
        EventB(y=x ** 2).send()
