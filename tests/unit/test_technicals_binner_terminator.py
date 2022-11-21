import os
import tempfile
from datetime import datetime
from unittest import TestCase
from unittest.mock import patch, mock_open

from entities.bucket import Bucket
from entities.candle import Candle
from entities.timespan import TimeSpan
from fakes.pipeline_validators import ValidationProcessor
from fakes.source import FakeSource
from pipeline.pipeline import Pipeline
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.technicals import TechnicalsProcessor
from pipeline.processors.technicals_buckets_matcher import TechnicalsBucketsMatcher, IndicatorsMatchedBuckets, \
    INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY
from pipeline.processors.technicals_normalizer import TechnicalsNormalizerProcessor, NormalizedIndicators, \
    NORMALIZED_INDICATORS_ATTACHMENT_KEY
from pipeline.runner import PipelineRunner
from pipeline.shared_context import SharedContext
from pipeline.terminators.technicals_binner import TechnicalsBinner
from unit import generate_candle_with_price, TEST_SYMBOL


class TestTechnicalsBinnerTerminator(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.source = FakeSource(
            [generate_candle_with_price(TimeSpan.Day, datetime.now(), c) for c in range(1, 80)])

    def test(self):
        cache_processor = CandleCache()
        technicals_normalizer = TechnicalsNormalizerProcessor(next_processor=cache_processor)
        technicals = TechnicalsProcessor(technicals_normalizer)

        with patch("builtins.open", mock_open()) as mock_file:
            binner_terminator = TechnicalsBinner([TEST_SYMBOL], 7, "/not/a/real/path.dat")
            PipelineRunner(Pipeline(self.source, technicals, binner_terminator)).run()

            mock_file.assert_called_with("/not/a/real/path.dat", 'w+')

    def test_matching_processor(self):
        def _check(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)
            context.put_kv_data('check_count', context.get_kv_data('check_count', 0) + 1)

            check_count = context.get_kv_data('check_count', 0)
            if check_count > 20:
                matched_buckets: IndicatorsMatchedBuckets = candle.attachments.get_attachment(
                    INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY)

                normalized_indicators: NormalizedIndicators = candle.attachments.get_attachment(
                    NORMALIZED_INDICATORS_ATTACHMENT_KEY)

                matched_bucket = matched_buckets.get('sma5')
                indicator_value = normalized_indicators.get('sma5')
                self.assertTrue(isinstance(matched_bucket, Bucket))
                self.assertTrue(matched_bucket.start <= indicator_value)
                self.assertTrue(matched_bucket.end > indicator_value)

        with tempfile.TemporaryDirectory() as tempdir:
            tmpfilepath = os.path.join(tempdir, 'temp_bin_file.dat')

            cache_processor = CandleCache()
            technicals_normalizer = TechnicalsNormalizerProcessor(next_processor=cache_processor)
            technicals = TechnicalsProcessor(technicals_normalizer)
            binner_terminator = TechnicalsBinner([TEST_SYMBOL], 7, tmpfilepath)

            PipelineRunner(Pipeline(self.source, technicals, binner_terminator)).run()

            validator = ValidationProcessor(_check)
            cache_processor = CandleCache(validator)
            matcher = TechnicalsBucketsMatcher(tmpfilepath, cache_processor)
            technicals_normalizer = TechnicalsNormalizerProcessor(next_processor=matcher)
            technicals = TechnicalsProcessor(technicals_normalizer)
            PipelineRunner(Pipeline(self.source, technicals)).run()
