from datetime import datetime
from typing import List, Dict
from unittest import TestCase

from entities.candle import Candle
from entities.timespan import TimeSpan
from fakes.source import FakeSource
from fakes.validator import ValidationProcessor
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
            cache_store: Dict[str, List[Candle]] = context.get_kv_data('cache')
            self.assertEqual(self.test_candle.symbol, cache_store[candle.symbol][0].symbol)

        validator = ValidationProcessor(_check)
        processor = CandleCache('cache', validator)
        PipelineRunner(self.source, processor).run()
