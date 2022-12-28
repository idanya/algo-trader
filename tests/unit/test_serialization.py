from datetime import datetime, timedelta
from unittest import TestCase

import mongomock

from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.processors.technicals_normalizer import TechnicalsNormalizerProcessor
from algotrader.pipeline.sources.mongodb_source import MongoDBSource
from algotrader.storage.mongodb_storage import MongoDBStorage


class TestSerialization(TestCase):
    def test_serialize_processor(self):
        candle_cache_processor = CandleCache(CandleCache())
        serialized = candle_cache_processor.serialize()
        self.assertEqual('algotrader.pipeline.processors.candle_cache:CandleCache', serialized['__class__'])
        self.assertEqual('algotrader.pipeline.processors.candle_cache:CandleCache', serialized['next_processor']['__class__'])

        deserialized: CandleCache = CandleCache.deserialize(serialized)
        self.assertIsNotNone(deserialized)
        self.assertIsInstance(deserialized, CandleCache)
        self.assertIsInstance(deserialized.next_processor, CandleCache)

    def test_serialize_with_ctor(self):
        tech_buckets_matcher = TechnicalsNormalizerProcessor(666)
        serialized = tech_buckets_matcher.serialize()

        deserialized: TechnicalsNormalizerProcessor = TechnicalsNormalizerProcessor.deserialize(serialized)
        self.assertEqual(666, deserialized.normalization_window_size)

    def test_serialize_with_nested_ctor(self):
        tech_buckets_matcher = TechnicalsNormalizerProcessor(666)
        candle_cache_processor = CandleCache(tech_buckets_matcher)
        serialized = candle_cache_processor.serialize()

        deserialized: CandleCache = CandleCache.deserialize(serialized)
        self.assertIsInstance(deserialized, CandleCache)
        self.assertIsInstance(deserialized.next_processor, TechnicalsNormalizerProcessor)
        self.assertEqual(deserialized.next_processor.normalization_window_size, 666)

    @mongomock.patch(servers=(('host', 666),))
    def test_serialize_complex_source(self):
        from_time = datetime.now() - timedelta(minutes=10)
        to_time = datetime.now()
        mongo_storage = MongoDBStorage('host', 666, 'db')
        mongo_source = MongoDBSource(mongo_storage, ['X', 'Y'], TimeSpan.Day, from_time, to_time)

        serialized = mongo_source.serialize()
        deserialized: MongoDBSource = MongoDBSource.deserialize(serialized)
        self.assertEqual('host', deserialized.mongo_storage.host)
        self.assertEqual(666, deserialized.mongo_storage.port)
        self.assertEqual('db', deserialized.mongo_storage.database)
        self.assertEqual(from_time, deserialized.from_time)
        self.assertEqual(to_time, deserialized.to_time)
