from datetime import datetime
from unittest import TestCase

from entities.candle import Candle
from entities.timespan import TimeSpan
from fakes.source import FakeSource
from fakes.pipeline_validators import ValidationProcessor
from pipeline.pipeline import Pipeline
from pipeline.processors.candle_cache import CandleCache
from pipeline.runner import PipelineRunner
from pipeline.shared_context import SharedContext
from unit import generate_candle


class TestCandleCacheProcessor(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.test_candle = generate_candle(TimeSpan.Day, datetime.now())
        self.source = FakeSource([self.test_candle])

    def test(self):
        def _check(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)

            cache_reader = CandleCache.context_reader(context)
            cached_candles = cache_reader.get_symbol_candles(candle.symbol)
            self.assertEqual(self.test_candle.symbol, cached_candles[0].symbol)

        validator = ValidationProcessor(_check)
        processor = CandleCache(validator)
        PipelineRunner(Pipeline(self.source, processor)).run()
