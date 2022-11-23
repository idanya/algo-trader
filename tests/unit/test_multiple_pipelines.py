from datetime import datetime, timedelta
from unittest import TestCase

from entities.timespan import TimeSpan
from fakes.pipeline_validators import TerminatorValidator
from pipeline.pipeline import Pipeline
from pipeline.processor import Processor
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.technicals import TechnicalsProcessor
from pipeline.processors.technicals_normalizer import TechnicalsNormalizerProcessor
from pipeline.runner import PipelineRunner
from pipeline.shared_context import SharedContext
from pipeline.sources.context_injection_factory_source import ContextInjectionFactorySource
from pipeline.sources.list_source import ListSource
from pipeline.terminators.last_candle_timestamp import LastSymbolTimestamp
from unit import generate_candle_with_price


class TestMultiplePipelines(TestCase):

    def setUp(self) -> None:
        super().setUp()

    def test_multiple_pipelines_list(self):
        def _check_pipeline_one(context: SharedContext):
            self.assertIsNotNone(context)
            context.put_kv_data('check', True)

        def _check_pipeline_two(context: SharedContext):
            self.assertIsNotNone(context)
            check = context.get_kv_data('check')
            self.assertTrue(check)

        source = ListSource([generate_candle_with_price(TimeSpan.Day, datetime.now(), 1)])
        processor = Processor()
        validator_one = TerminatorValidator(_check_pipeline_one)
        validator_two = TerminatorValidator(_check_pipeline_two)

        pipeline_one = Pipeline(source, processor, validator_one)
        pipeline_two = Pipeline(source, processor, validator_two)

        pipelines = [pipeline_one, pipeline_two]

        PipelineRunner(pipelines).run()

    def test_multiple_pipelines_shared_context(self):
        from_time = datetime.fromtimestamp(1669093200)
        candle_length = 250
        half_length = int(candle_length / 2)
        overlap_index = int((half_length - (0.1 * candle_length)))
        symbols = ['X']

        # Create our injectable context
        context = SharedContext()

        # Create our first pipeline with our injected context and cache processor.
        def _check(context: SharedContext):
            self.assertEqual(candle_length, len(CandleCache.context_reader(context).get_symbol_candles(symbols[0])))

        candles = [generate_candle_with_price(TimeSpan.Minute, from_time - timedelta(minutes=c), c) for c in range(candle_length)]
        source = ListSource(candles[half_length:])

        pipeline_one = Pipeline(source, CandleCache(), LastSymbolTimestamp(symbols))

        # In production you would calculate `from_time` based on LastSymbolTimestamp and also have a sink processor to save new results.
        # We use a ContextInjectionFactorySource to inject the context back into a constructor.
        def _create_context_injection_factory_source(context: SharedContext):
            self.assertEqual(from_time - timedelta(minutes=candle_length / 2), LastSymbolTimestamp.get(context))
            return ListSource(candles[:-overlap_index])

        source = ContextInjectionFactorySource(context, _create_context_injection_factory_source)

        # Create our second pipeline with some overlapping candles and our technical processors
        cache_processor = CandleCache()
        technical_normalizer = TechnicalsNormalizerProcessor(next_processor=cache_processor)
        technicals = TechnicalsProcessor(technical_normalizer)

        pipeline_two = Pipeline(source, technicals, TerminatorValidator(_check))

        # Finally we run the pipelines as a list.
        PipelineRunner([pipeline_one, pipeline_two], context).run()
