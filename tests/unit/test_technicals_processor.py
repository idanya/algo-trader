from datetime import datetime
from unittest import TestCase

from entities.candle import Candle
from entities.timespan import TimeSpan
from fakes.pipeline_validators import ValidationProcessor
from fakes.source import FakeSource
from pipeline.pipeline import Pipeline
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.technicals import TechnicalsProcessor, INDICATORS_ATTACHMENT_KEY, Indicators
from pipeline.processors.technicals_normalizer import TechnicalsNormalizerProcessor, \
    NORMALIZED_INDICATORS_ATTACHMENT_KEY, NormalizedIndicators
from pipeline.runner import PipelineRunner
from pipeline.shared_context import SharedContext
from unit import generate_candle_with_price


class TestTechnicalsProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = FakeSource(
            [generate_candle_with_price(TimeSpan.Day, datetime.now(), c) for c in range(1, 50)])

    def test(self):
        def _check(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)
            context.put_kv_data('check_count', context.get_kv_data('check_count', 0) + 1)

            check_count = context.get_kv_data('check_count', 0)
            if check_count > 20:
                candle_indicators: Indicators = candle.attachments.get_attachment(
                    INDICATORS_ATTACHMENT_KEY)
                macd_values = candle_indicators.get('macd')
                self.assertEqual(len(macd_values), 3)
                self.assertIsNotNone(macd_values[0])
                self.assertIsNotNone(macd_values[1])
                self.assertIsNotNone(macd_values[2])

                sma5_value = candle_indicators.get('sma5')
                self.assertTrue(sma5_value > 0)

                cci7_value = candle_indicators.get('cci7')
                self.assertIsNotNone(cci7_value)

        validator = ValidationProcessor(_check)
        cache_processor = CandleCache(validator)
        processor = TechnicalsProcessor(cache_processor)
        PipelineRunner(Pipeline(self.source, processor)).run()

    def test_normalization(self):
        def _check(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)
            context.put_kv_data('check_count', context.get_kv_data('check_count', 0) + 1)

            check_count = context.get_kv_data('check_count', 0)
            if check_count > 20:
                indicators: Indicators = candle.attachments.get_attachment(
                    INDICATORS_ATTACHMENT_KEY)

                normalized_indicators: NormalizedIndicators = candle.attachments.get_attachment(
                    NORMALIZED_INDICATORS_ATTACHMENT_KEY)
                sma5_value = indicators.get('sma5')
                normalized_sma5_value = normalized_indicators.get('sma5')
                vwap = (candle.close + candle.high + candle.low) / candle.volume
                self.assertTrue(sma5_value / vwap, normalized_sma5_value)

        validator = ValidationProcessor(_check)
        cache_processor = CandleCache(validator)
        technicals_normalizer = TechnicalsNormalizerProcessor(next_processor=cache_processor)
        technicals = TechnicalsProcessor(technicals_normalizer)
        PipelineRunner(Pipeline(self.source, technicals)).run()
