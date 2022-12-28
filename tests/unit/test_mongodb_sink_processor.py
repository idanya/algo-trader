import random
from datetime import datetime, timedelta
from unittest import TestCase

import mongomock

from algotrader.entities.timespan import TimeSpan
from fakes.pipeline_validators import TerminatorValidator
from fakes.source import FakeSource
from algotrader.pipeline.pipeline import Pipeline
from algotrader.pipeline.processors.storage_provider_sink import StorageSinkProcessor
from algotrader.pipeline.runner import PipelineRunner
from algotrader.pipeline.shared_context import SharedContext
from algotrader.storage.mongodb_storage import MongoDBStorage
from unit import generate_candle_with_price, TEST_SYMBOL


class TestMongoDBSinkProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = FakeSource(
            [generate_candle_with_price(TimeSpan.Day, datetime.now() - timedelta(minutes=c), random.randint(0, c)) for c
             in range(1, 50)])

    @mongomock.patch(servers=(('localhost', 27017),))
    def test(self):
        mogodb_storage = MongoDBStorage()
        mogodb_storage.__drop_collections__()

        def _check(context: SharedContext):
            self.assertIsNotNone(context)
            candles = mogodb_storage.get_symbol_candles(TEST_SYMBOL, TimeSpan.Day,
                                                        datetime.now() - timedelta(days=1),
                                                        datetime.now())
            self.assertEqual(49, len(candles))

        validator = TerminatorValidator(_check)
        processor = StorageSinkProcessor(mogodb_storage)
        PipelineRunner(Pipeline(self.source, processor, validator)).run()
