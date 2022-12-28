import json
import os
import random
import tempfile
from datetime import datetime
from unittest import TestCase

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from fakes.pipeline_validators import TerminatorValidator
from fakes.source import FakeSource
from algotrader.pipeline.pipeline import Pipeline
from algotrader.pipeline.processors.file_sink import FileSinkProcessor
from algotrader.pipeline.runner import PipelineRunner
from algotrader.pipeline.shared_context import SharedContext
from unit import generate_candle_with_price


class TestFileSinkProcessor(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.source = FakeSource(
            [generate_candle_with_price(TimeSpan.Day, datetime.now(), random.randint(0, c)) for c in range(1, 50)])

    def test(self):
        temp_file = tempfile.NamedTemporaryFile(delete=False)

        def _check(context: SharedContext):
            self.assertIsNotNone(context)
            lines = temp_file.readlines()
            self.assertEqual(49, len(lines))
            for line in lines:
                candle = Candle.deserialize(json.loads(line))
                self.assertEqual(TimeSpan.Day, candle.time_span)
                self.assertEqual(datetime.now().day, candle.timestamp.day)

        validator = TerminatorValidator(_check)

        processor = FileSinkProcessor(temp_file.name)
        PipelineRunner(Pipeline(self.source, processor, validator)).run()

        temp_file.close()
        os.unlink(temp_file.name)
