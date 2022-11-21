from datetime import datetime, timedelta
from unittest import TestCase

from entities.candle import Candle
from entities.event import Event
from entities.timespan import TimeSpan
from fakes.pipeline_validators import ValidationProcessor, TerminatorValidator
from fakes.source import FakeSource
from pipeline.pipeline import Pipeline
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.timespan_change import TimeSpanChangeProcessor
from pipeline.runner import PipelineRunner
from pipeline.shared_context import SharedContext
from unit import generate_candle_with_price


class TestTimeSpanChangeProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = FakeSource(
            [generate_candle_with_price(TimeSpan.Day, datetime.fromtimestamp(1669050000) - timedelta(hours=c), c) for c in range(1, 55)])

    def test(self):
        def _terminate(context: SharedContext):
            self.assertIsNotNone(context)
            event_count = context.get_kv_data('event_count', 0)
            candle_count = context.get_kv_data('candle_count', 0)
            self.assertEqual(event_count, 2)
            self.assertEqual(candle_count, 54)

        def _process(context: SharedContext, candle: Candle):
            self.assertIsNotNone(context)
            context.put_kv_data('candle_count', context.get_kv_data('candle_count', 0) + 1)

        def _event(context: SharedContext, event: Event):
            self.assertIsNotNone(context)

            if event != Event.TimeSpanChange:
                return

            context.put_kv_data('event_count', context.get_kv_data('event_count', 0) + 1)

            candle_count = context.get_kv_data('candle_count', 0)
            self.assertTrue(candle_count > 0)

        terminator = TerminatorValidator(_terminate)

        validator = ValidationProcessor(_process, _event)
        cache_processor = CandleCache(validator)
        processor = TimeSpanChangeProcessor(TimeSpan.Day, cache_processor)
        PipelineRunner(Pipeline(self.source, processor, terminator)).run()
