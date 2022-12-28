from datetime import datetime
from unittest import TestCase

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from fakes.pipeline_validators import ValidationProcessor
from fakes.source import FakeSource
from algotrader.pipeline.pipeline import Pipeline
from algotrader.pipeline.reverse_source import ReverseSource
from algotrader.pipeline.runner import PipelineRunner
from algotrader.pipeline.shared_context import SharedContext
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
