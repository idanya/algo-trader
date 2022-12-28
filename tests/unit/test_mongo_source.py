from datetime import datetime, timedelta
from unittest import TestCase

import mongomock

from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.sources.mongodb_source import MongoDBSource
from algotrader.storage.mongodb_storage import MongoDBStorage
from unit import generate_candle, TEST_SYMBOL


class TestMongoSource(TestCase):
    @mongomock.patch(servers=(('localhost', 27017),))
    def setUp(self) -> None:
        super().setUp()
        self.mongo_storage = MongoDBStorage()
        self.mongo_storage.__drop_collections__()

    def test(self):
        for i in range(10):
            self.mongo_storage.save(generate_candle(TimeSpan.Day, datetime.now() - timedelta(minutes=i)))

        from_time = datetime.now() - timedelta(days=1)
        to_time = datetime.now()
        source = MongoDBSource(self.mongo_storage, [TEST_SYMBOL], TimeSpan.Day, from_time, to_time)

        candles = list(source.read())
        self.assertEqual(len(candles), 10)

        for candle in candles:
            self.assertEqual(TEST_SYMBOL, candle.symbol)
            self.assertEqual(TimeSpan.Day, candle.time_span)
            self.assertTrue(candle.timestamp < datetime.now())
