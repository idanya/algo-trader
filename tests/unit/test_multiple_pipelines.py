from datetime import datetime
from unittest import TestCase

from algotrader.entities.timespan import TimeSpan
from fakes.pipeline_validators import TerminatorValidator
from fakes.source import FakeSource
from algotrader.pipeline.pipeline import Pipeline
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.runner import PipelineRunner
from algotrader.pipeline.shared_context import SharedContext
from unit import generate_candle_with_price


class TestMultiplePipelines(TestCase):

    def setUp(self) -> None:
        super().setUp()

    def test_multiple_pipelines(self):
        def _check_pipeline_one(context: SharedContext):
            self.assertIsNotNone(context)
            context.put_kv_data('check', True)

        def _check_pipeline_two(context: SharedContext):
            self.assertIsNotNone(context)
            check = context.get_kv_data('check')
            self.assertTrue(check)

        source = FakeSource([generate_candle_with_price(TimeSpan.Day, datetime.now(), 1)])
        processor = Processor()
        validator_one = TerminatorValidator(_check_pipeline_one)
        validator_two = TerminatorValidator(_check_pipeline_two)

        pipeline_one = Pipeline(source, processor, validator_one)
        pipeline_two = Pipeline(source, processor, validator_two)

        pipelines = [pipeline_one, pipeline_two]

        PipelineRunner(pipelines).run()
