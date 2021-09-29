from datetime import datetime
from typing import Dict
from unittest import TestCase

from entities.candle import Candle
from entities.serializable import Serializable, Deserializable
from entities.timespan import TimeSpan
from unit import generate_candle_with_price


class TestSerializations(TestCase):
    def test_candle(self):
        candle = generate_candle_with_price(TimeSpan.Day, datetime.now(), 888)
        data = candle.serialize()

        new_candle = Candle.deserialize(data)

        self.assertEqual(candle.symbol, new_candle.symbol)
        self.assertEqual(candle.timestamp, new_candle.timestamp)
        self.assertEqual(candle.time_span, new_candle.time_span)
        self.assertEqual(candle.close, new_candle.close)
        self.assertEqual(candle.high, new_candle.high)
        self.assertEqual(candle.low, new_candle.low)
        self.assertEqual(candle.volume, new_candle.volume)
        self.assertEqual(candle.open, new_candle.open)

    def test_candle_attachments(self):
        class NothingClass(Serializable, Deserializable):

            def __init__(self) -> None:
                super().__init__()

            @classmethod
            def deserialize(cls, data: Dict):
                return NothingClass()

            def serialize(self) -> Dict:
                obj = super().serialize()
                obj.update({
                    '__class__': self.__class__.__name__,
                    'nothing': 'at-all'
                })
                return obj

        candle = generate_candle_with_price(TimeSpan.Day, datetime.now(), 888)
        candle.add_attachement('key1', NothingClass())

        data = candle.serialize()
        new_candle = Candle.deserialize(data)

        self.assertEqual(candle.symbol, new_candle.symbol)
        original_attachment = candle.attachments.get_attachment('key1')
        new_attachment = new_candle.attachments.get_attachment('key1')
        self.assertEqual(original_attachment.__class__, new_attachment.__class__)
