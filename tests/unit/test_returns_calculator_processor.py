import random
from datetime import datetime
from unittest import TestCase

from entities.candle import Candle
from entities.timespan import TimeSpan
from fakes.pipeline_validators import ValidationProcessor
from fakes.source import FakeSource
from pipeline.pipeline import Pipeline
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.returns import ReturnsCalculatorProcessor, RETURNS_ATTACHMENT_KEY, Returns
from pipeline.runner import PipelineRunner
from pipeline.shared_context import SharedContext
from unit import generate_candle_with_price


class TestReturnsCalculatorProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = FakeSource(
            [generate_candle_with_price(TimeSpan.Day, datetime.now(), random.randint(1, c)) for c in range(1, 50)])

    def test(self):
        def _check(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)
            context.put_kv_data('check_count', context.get_kv_data('check_count', 0) + 1)
            check_count = context.get_kv_data('check_count', 0)

            if check_count > 6:
                candle_returns: Returns = candle.attachments.get_attachment(RETURNS_ATTACHMENT_KEY)
                self.assertTrue(candle_returns.has('ctc1'))

        validator = ValidationProcessor(_check)
        cache_processor = CandleCache(validator)
        processor = ReturnsCalculatorProcessor(cache_processor)
        PipelineRunner(Pipeline(self.source, processor)).run()
