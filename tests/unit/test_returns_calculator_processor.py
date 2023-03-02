from datetime import datetime, timedelta
from unittest import TestCase

from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.pipeline import Pipeline
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.processors.returns import ReturnsCalculatorProcessor, RETURNS_ATTACHMENT_KEY
from algotrader.pipeline.reverse_source import ReverseSource
from algotrader.pipeline.runner import PipelineRunner
from algotrader.pipeline.shared_context import SharedContext
from fakes.pipeline_validators import TerminatorValidator
from fakes.source import FakeSource
from unit import generate_candle_with_price, TEST_SYMBOL


class TestReturnsCalculatorProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = FakeSource(
            [generate_candle_with_price(TimeSpan.Day, datetime.now() + timedelta(minutes=c), c) for c in range(1, 50)])

    def test(self):
        def _check_returns(context: SharedContext):
            self.assertIsNotNone(context)
            cache_reader = CandleCache.context_reader(context)
            candles = cache_reader.get_symbol_candles(TEST_SYMBOL)

            self.assertFalse(candles[0].attachments.get_attachment(RETURNS_ATTACHMENT_KEY).has('ctc-1'))
            self.assertFalse(candles[1].attachments.get_attachment(RETURNS_ATTACHMENT_KEY).has('ctc-1'))
            self.assertFalse(candles[2].attachments.get_attachment(RETURNS_ATTACHMENT_KEY).has('ctc-1'))

            ctc1 = candles[3].attachments.get_attachment(RETURNS_ATTACHMENT_KEY)['ctc-1']
            ctc2 = candles[3].attachments.get_attachment(RETURNS_ATTACHMENT_KEY)['ctc-2']
            ctc3 = candles[3].attachments.get_attachment(RETURNS_ATTACHMENT_KEY)['ctc-3']
            self.assertTrue(ctc1 < ctc2 < ctc3)

        cache_processor = CandleCache()
        processor = ReturnsCalculatorProcessor('ctc', 3, cache_processor)

        terminator = TerminatorValidator(_check_returns)

        self.source = ReverseSource(self.source)
        PipelineRunner(Pipeline(self.source, processor, terminator)).run()
