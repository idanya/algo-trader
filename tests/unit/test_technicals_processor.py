import random
from datetime import datetime
from unittest import TestCase

from entities.candle import Candle
from entities.timespan import TimeSpan
from fakes.source import FakeSource
from fakes.pipeline_validators import ValidationProcessor
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.technicals import TechnicalsProcessor
from pipeline.runner import PipelineRunner
from pipeline.shared_context import SharedContext
from unit import generate_candle_with_price


class TestTechnicalsProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = FakeSource(
            [generate_candle_with_price(TimeSpan.Day, datetime.now(), random.randint(1, c)) for c in range(1, 50)])

    def test(self):
        def _check(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)
            context.put_kv_data('check_count', context.get_kv_data('check_count', 0) + 1)

            check_count = context.get_kv_data('check_count', 0)
            if check_count > 13:
                tech_reader = TechnicalsProcessor.context_reader(context)

                macd_values = tech_reader.get_indicator_values(candle.symbol, 'macd')
                self.assertEqual(len(macd_values), 3)
                self.assertEqual(len(macd_values[0]), check_count - 4)
                self.assertEqual(len(macd_values[1]), check_count - 4)
                self.assertEqual(len(macd_values[2]), check_count - 4)

                sma5_values = tech_reader.get_indicator_values(candle.symbol, 'sma5')
                self.assertEqual(len(sma5_values), check_count - 4)

                cci7_values = tech_reader.get_indicator_values(candle.symbol, 'cci7')
                self.assertEqual(len(cci7_values), check_count - 12)

        validator = ValidationProcessor(_check)
        technicals_processor = TechnicalsProcessor(validator)
        processor = CandleCache(technicals_processor)
        PipelineRunner(self.source, processor).run()
