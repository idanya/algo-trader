import os
import random
from datetime import datetime, timedelta
from typing import List
from unittest import TestCase

from entities.candle import Candle
from entities.timespan import TimeSpan
from fakes.pipeline_validators import ValidationProcessor
from fakes.source import FakeSource
from pipeline.pipeline import Pipeline
from pipeline.processors.assets_correlation import AssetCorrelation, CORRELATIONS_ATTACHMENT_KEY, \
    AssetCorrelationProcessor
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.technicals import TechnicalsProcessor
from pipeline.processors.timespan_change import TimeSpanChangeProcessor
from pipeline.runner import PipelineRunner
from pipeline.shared_context import SharedContext
from unit import generate_candle_with_price_and_symbol


class TestAssetCorrelationProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()
        x = [generate_candle_with_price_and_symbol('X', TimeSpan.Day, datetime.now() - timedelta(days=c),
                                                   c + random.randint(1, 10)) for c in range(1, 49)]
        y = [generate_candle_with_price_and_symbol('Y', TimeSpan.Day, datetime.now() - timedelta(days=c),
                                                   c + random.randint(1, 10)) for c in range(1, 49)]
        z = [generate_candle_with_price_and_symbol('Z', TimeSpan.Day, datetime.now() - timedelta(days=c),
                                                   c + random.randint(1, 10)) for c in range(1, 49)]

        merged: List[Candle] = []
        for i in range(len(x)):
            merged.append(x[i])
            merged.append(y[i])
            merged.append(z[i])

        self.source = FakeSource(merged)

    def test_correlation(self):
        def _check(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)
            context.put_kv_data('check_count', context.get_kv_data('check_count', 0) + 1)

            check_count = context.get_kv_data('check_count', 0)
            if check_count > 20:
                cache_reader = CandleCache.context_reader(context)
                latest_candle = cache_reader.get_symbol_candles(candle.symbol)[-2]
                asset_correlation: AssetCorrelation = latest_candle.attachments.get_attachment(
                    CORRELATIONS_ATTACHMENT_KEY)
                if candle.symbol == 'X':
                    self.assertFalse(asset_correlation.has('X'))
                    self.assertTrue(asset_correlation.has('Y'))
                    self.assertTrue(asset_correlation.has('Z'))
                else:
                    self.assertTrue(asset_correlation.has('X'))

        validator = ValidationProcessor(_check)
        cache_processor = CandleCache(validator)
        correlations_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                              '../configs/correlations.json')
        asset_correlation = AssetCorrelationProcessor(correlations_file_path, cache_processor)
        timespan_change_processor = TimeSpanChangeProcessor(TimeSpan.Day, asset_correlation)
        technicals = TechnicalsProcessor(timespan_change_processor)
        PipelineRunner(Pipeline(self.source, technicals)).run()
