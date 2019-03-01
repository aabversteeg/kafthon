import time
import atexit

import docker


class KafkaRunner():
    instance_name = 'kafka'
    docker_client = docker.from_env()

    def __init__(self):
        self._kafka_container = None
        atexit.register(self.remove_container)

    def run(self):
        if self._kafka_container is None:
            self.remove_container()

            self._kafka_container = self.docker_client.containers.run(
                image='spotify/kafka',
                name=self.instance_name,
                environment=dict(
                    KAFKA_AUTO_CREATE_TOPICS_ENABLE=True,
                ),
                detach=True,
                network='host'
            )
            time.sleep(5)

    def remove_container(self):
        try:
            container = self.docker_client.containers.get(self.instance_name)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass
    __del__ = remove_container


kafka_runner = KafkaRunner()
