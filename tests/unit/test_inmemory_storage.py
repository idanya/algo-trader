import unittest
from datetime import datetime
from typing import List

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.storage.inmemory_storage import InMemoryStorage
from unit import generate_candle, TEST_SYMBOL


class TestInMemoryStorage(unittest.TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.inmemory_storage = InMemoryStorage()

    def test_save_single_candle(self):
        minute_candle = generate_candle(TimeSpan.Minute, datetime.now())

        self.inmemory_storage.save(minute_candle)

        candles: List[Candle] = self.inmemory_storage.get_symbol_candles(symbol=TEST_SYMBOL, time_span=TimeSpan.Minute,
                                                                         from_timestamp=minute_candle.timestamp,
                                                                         to_timestamp=minute_candle.timestamp)

        self.assertEqual(1, len(candles))
        self.assertEqual(TEST_SYMBOL, candles[0].symbol)
        self.assertEqual(TimeSpan.Minute, candles[0].time_span)
        self.assertEqual(minute_candle.timestamp, candles[0].timestamp)

    def test_save_different_timespans_candle(self):
        minute_candle = generate_candle(TimeSpan.Minute, datetime.now())
        self.inmemory_storage.save(minute_candle)

        day_candle = generate_candle(TimeSpan.Day, minute_candle.timestamp)
        self.inmemory_storage.save(day_candle)

        candles: List[Candle] = self.inmemory_storage.get_symbol_candles(symbol=TEST_SYMBOL, time_span=TimeSpan.Minute,
                                                                         from_timestamp=minute_candle.timestamp,
                                                                         to_timestamp=minute_candle.timestamp)

        self.assertEqual(1, len(candles))
        self.assertEqual(TimeSpan.Minute, candles[0].time_span)
        self.assertEqual(minute_candle.timestamp, candles[0].timestamp)
