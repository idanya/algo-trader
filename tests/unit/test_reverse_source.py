from datetime import datetime
from unittest import TestCase

from entities.candle import Candle
from entities.timespan import TimeSpan
from fakes.pipeline_validators import ValidationProcessor
from fakes.source import FakeSource
from pipeline.pipeline import Pipeline
from pipeline.reverse_source import ReverseSource
from pipeline.runner import PipelineRunner
from pipeline.shared_context import SharedContext
from unit import generate_candle_with_price


class TestReverseSource(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.source = FakeSource(
            [generate_candle_with_price(TimeSpan.Day, datetime.now(), c) for c in range(1, 50)])

    def test_regular_order(self):
        def _check(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)

            last_price = context.get_kv_data('last_price')
            if last_price:
                self.assertTrue(candle.close > last_price)

            context.put_kv_data('last_price', candle.close)

        validator = ValidationProcessor(_check)
        PipelineRunner(Pipeline(self.source, validator)).run()

    def test_reverse_order(self):
        def _check(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)

            last_price = context.get_kv_data('last_price')
            if last_price:
                self.assertTrue(candle.close < last_price)

            context.put_kv_data('last_price', candle.close)

        validator = ValidationProcessor(_check)
        PipelineRunner(Pipeline(ReverseSource(self.source), validator)).run()
