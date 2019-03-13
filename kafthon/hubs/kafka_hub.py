import logging
import datetime

from kafka import KafkaConsumer, KafkaProducer

from ..events import BaseEvent
from ..serializers import MsgpackSerializer
from .base_hub import BaseHub
from ..utils import get_cls_path


logger = logging.getLogger(__name__)


class KafkaHub(BaseHub):
    def __init__(self, bootstrap_servers):
        super().__init__()

        self.bootstrap_servers = bootstrap_servers

        self._producer = None
        self._consumer = None

    @property
    def consumer(self):
        if self._consumer is None:
            self._consumer = KafkaConsumer(
                *self.get_topics(),
                bootstrap_servers=self.bootstrap_servers,
                value_deserializer=MsgpackSerializer.deserialize
            )
        return self._consumer

    @property
    def producer(self):
        if self._producer is None:
            self._producer = KafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=MsgpackSerializer.serialize
            )
        return self._producer

    def subscribe(self, event_type, func, unwrap=True):
        super().subscribe(event_type, func, unwrap=unwrap)

        new_topics = self.get_topics() - self.consumer.subscription()
        if new_topics:
            self.consumer.subscribe(new_topics)

    def get_topics(self):
        return {
            get_cls_path(event_type)
            for event_type, subscription_set in self._subscriptions.items()
            if subscription_set
        }

    def send(self, event):
        if not isinstance(event, BaseEvent):
            raise TypeError('The event argument must be an instance of BaseEvent.')

        topic_name = get_cls_path(
            type(event)
        )
        print('Sending event:', topic_name, str(event)[:100])

        self.producer.send(
            topic_name,
            event
        )
        self.producer.flush()

    def start_receiving(self, timeout_ms=None, max_records=None):
        if not (timeout_ms is None and max_records is None):
            response = self.consumer.poll(
                timeout_ms=timeout_ms or 0,
                max_records=max_records
            )
            event_generator = (
                event
                for event_list in response.values()
                for event in event_list
            )
        else:
            event_generator = self.consumer

        for raw_event in event_generator:
            event_type = self._kafthon_app.get_event_type_by_cls_path(raw_event.topic)
            if event_type is None:
                print('Could not infer even type for:', raw_event.topic)

            event = event_type(raw_event.value)
            print('Received event:', str(event)[:300])

            event_time = event.get('event_time')
            if event_time:
                latency = datetime.datetime.now() - event_time
                print(f'Latency: {latency}')

            self._invoke_handlers(event)

    def __del__(self):
        self.close()

    def perform_reset(self):
        super().perform_reset()
        self.close()

    def close(self):
        if self._producer is not None and not self._producer._closed:
            self._producer.close(timeout=3)
            self._producer = None

        if self._consumer is not None and not self._consumer._closed:
            self._consumer.close()
            self._consumer = None


__all__ = ['KafkaHub']
