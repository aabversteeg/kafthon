import logging
import datetime

from kafka import KafkaConsumer, KafkaProducer

from ..events import BaseEvent
from ..serializers import MsgpackSerializer
from .base_hub import BaseHub


logger = logging.getLogger(__name__)


class KafkaHub(BaseHub):
    def __init__(self, bootstrap_servers):
        super().__init__()

        self.bootstrap_servers = bootstrap_servers

        self._producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=MsgpackSerializer.serialize
        )
        self._consumer = None

    def _make_consumer(self):
        self._consumer = KafkaConsumer(
            *self.get_topics(),
            bootstrap_servers=self.bootstrap_servers,
            value_deserializer=MsgpackSerializer.deserialize
        )

    def subscribe(self, event_type, func, unwrap=True):
        super().subscribe(event_type, func, unwrap=unwrap)

        if not self._consumer:
            self._make_consumer()
        else:
            new_topics = self.get_topics() - self._consumer.subscription()
            if new_topics:
                self._consumer.subscribe(new_topics)

    def get_topics(self):
        return {
            event_type.get_topic_name()
            for event_type, handlers in self._listeners.items()
            if handlers
        }

    def send(self, event):
        print('Sending event: %s', str(event)[:100])
        if not isinstance(event, BaseEvent):
            raise TypeError('The event argument must be an instance of BaseEvent.')

        self._producer.send(
            event.get_topic_name(),
            event
        )
        self._producer.flush()

    def start_receiving(self, **kwargs):
        if not self._listeners:
            return

        self._make_consumer()

        for event in self._consumer:
            print('Received event: %s', str(event.value)[:300])

            event_time = event.value.get('event_time')
            if event_time:
                latency = datetime.datetime.now() - event_time
                print(f'Latency: {latency}')

            self._invoke_handlers(event.value)

    def fetch_one(self, timeout_ms=100, max_records=1):
        if not self._consumer:
            self._make_consumer()

        response = self._consumer.poll(
            timeout_ms=timeout_ms,
            max_records=max_records
        )
        for event_list in response.values():
            for event in event_list:
                print('Received event: %s', str(event.value)[:300])
                self._invoke_handlers(event.value)

    def __del__(self):
        self.close()

    def close(self):
        if hasattr(self, '_producer') and not getattr(self._producer, '_closed', False):
            self._producer.close(timeout=0)


__all__ = ['KafkaHub']
