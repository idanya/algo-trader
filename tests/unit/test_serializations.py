from datetime import datetime
from unittest import TestCase

from entities.candle import Candle
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
