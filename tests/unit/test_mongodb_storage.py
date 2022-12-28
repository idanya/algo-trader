from datetime import datetime, timedelta
from typing import List
from unittest import TestCase

import mongomock

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.storage.mongodb_storage import MongoDBStorage
from unit import generate_candle, TEST_SYMBOL


class TestMongoDBStorage(TestCase):
    @mongomock.patch(servers=(('localhost', 27017),))
    def setUp(self) -> None:
        super().setUp()
        self.mogodb_storage = MongoDBStorage()
        self.mogodb_storage.__drop_collections__()

    def test_save_single_candle(self):
        minute_candle = generate_candle(TimeSpan.Minute, datetime.now().replace(microsecond=0))

        self.mogodb_storage.save(minute_candle)

        candles: List[Candle] = self.mogodb_storage.get_symbol_candles(symbol=TEST_SYMBOL, time_span=TimeSpan.Minute,
                                                                       from_timestamp=minute_candle.timestamp,
                                                                       to_timestamp=minute_candle.timestamp)

        self.assertEqual(1, len(candles))
        self.assertEqual(TEST_SYMBOL, candles[0].symbol)
        self.assertEqual(TimeSpan.Minute, candles[0].time_span)
        self.assertEqual(minute_candle.timestamp, candles[0].timestamp)

    def test_save_different_timespans_candle(self):
        minute_candle = generate_candle(TimeSpan.Minute, datetime.now().replace(microsecond=0))
        self.mogodb_storage.save(minute_candle)

        day_candle = generate_candle(TimeSpan.Day, minute_candle.timestamp.replace(microsecond=0))
        self.mogodb_storage.save(day_candle)

        candles: List[Candle] = self.mogodb_storage.get_symbol_candles(symbol=TEST_SYMBOL, time_span=TimeSpan.Minute,
                                                                       from_timestamp=minute_candle.timestamp,
                                                                       to_timestamp=minute_candle.timestamp)

        self.assertEqual(1, len(candles))
        self.assertEqual(TimeSpan.Minute, candles[0].time_span)
        self.assertEqual(minute_candle.timestamp, candles[0].timestamp)

    def test_sorted_results(self):
        minute_candle = generate_candle(TimeSpan.Minute, datetime.now().replace(microsecond=0))
        next_minute_candle = generate_candle(TimeSpan.Minute,
                                             (datetime.now() + timedelta(minutes=1)).replace(microsecond=0))

        self.mogodb_storage.save(next_minute_candle)
        self.mogodb_storage.save(minute_candle)

        candles: List[Candle] = self.mogodb_storage.get_symbol_candles(symbol=TEST_SYMBOL, time_span=TimeSpan.Minute,
                                                                       from_timestamp=minute_candle.timestamp,
                                                                       to_timestamp=next_minute_candle.timestamp)

        self.assertEqual(2, len(candles))
        self.assertEqual(candles[0].timestamp, minute_candle.timestamp)
        self.assertEqual(candles[1].timestamp, next_minute_candle.timestamp)
