import time
import atexit

import kafka
import docker


class KafkaRunner():
    instance_name = 'kafka'
    docker_client = docker.from_env()

    def __init__(self):
        self._kafka_container = None
        atexit.register(self.remove_container)

    def run(self):
        if self._kafka_container is None:
            self.remove_container(force=True)

            self._kafka_container = self.docker_client.containers.run(
                image='spotify/kafka',
                name=self.instance_name,
                environment=dict(
                    KAFKA_AUTO_CREATE_TOPICS_ENABLE=True,
                ),
                detach=True,
                network='host'
            )

        self.check_connection()

    def check_connection(self):
        for i in range(10):
            try:
                kafka.KafkaProducer(
                    bootstrap_servers='localhost:9092'
                )
            except kafka.errors.NoBrokersAvailable:
                print('Trying to connect to Kafka')
                time.sleep(.5)
            else:
                print('Connection to Kafka was established')
                break

    def remove_container(self, force=False):
        if not force and self._kafka_container is None:
            return

        try:
            container = self.docker_client.containers.get(self.instance_name)
            container.remove(force=True)
        except docker.errors.NotFound:
            pass
        else:
            self._kafka_container = None

    __del__ = remove_container


kafka_runner = KafkaRunner()
