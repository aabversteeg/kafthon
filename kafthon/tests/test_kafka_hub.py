# from unittest.mock import MagicMock

# import pytest

# from ..events.base import BaseEvent
# from ..hubs.kafka import KafkaHub


# @pytest.mark.integration
# class TestEventSending(object):
#     def test(self):

#         class TestEvent(BaseEvent):
#             event_hub = KafkaHub(['kafka:9092'])

#         mock = MagicMock()

#         TestEvent.subscribe(
#             mock,
#             unwrap=False
#         )

#         mock.assert_not_called()

#         TestEvent.event_hub.fetch_one()

#         msg = TestEvent(x=5, y=1)
#         msg.send()

#         TestEvent.event_hub.fetch_one()

#         mock.assert_called_once()
#         assert msg == mock.call_args[0][0]

#         TestEvent.event_hub.close()
