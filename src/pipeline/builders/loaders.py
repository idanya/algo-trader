from datetime import datetime, timedelta

from assets.assets_provider import AssetsProvider
from entities.timespan import TimeSpan
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.mongodb_sink import MongoDBSinkProcessor
from pipeline.processors.returns import ReturnsCalculatorProcessor
from pipeline.processors.technicals import TechnicalsProcessor
from pipeline.processors.technicals_normalizer import TechnicalsNormalizerProcessor
from pipeline.reverse_source import ReverseSource
from pipeline.runner import PipelineRunner
from pipeline.sources.ib_history import IBHistorySource
from pipeline.sources.mongodb_source import MongoDBSource
from providers.ib.interactive_brokers_connector import InteractiveBrokersConnector
from storage.mongodb_storage import MongoDBStorage


class LoadersPipelines:
    @staticmethod
    def build_daily_loader() -> PipelineRunner:
        mongodb_storage = MongoDBStorage()

        from_time = datetime.now() - timedelta(days=365 * 3)
        symbols = AssetsProvider.get_sp500_symbols()

        source = IBHistorySource(InteractiveBrokersConnector(), symbols, TimeSpan.Day, from_time)

        sink = MongoDBSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = TechnicalsProcessor(cache_processor)

        return PipelineRunner(source, processor)

    @staticmethod
    def build_returns_calculator() -> PipelineRunner:
        mongodb_storage = MongoDBStorage()
        symbols = AssetsProvider.get_sp500_symbols()

        from_time = datetime.now() - timedelta(days=365 * 2)
        source = MongoDBSource(mongodb_storage, symbols, TimeSpan.Day, from_time)
        source = ReverseSource(source)

        sink = MongoDBSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = ReturnsCalculatorProcessor(cache_processor)

        return PipelineRunner(source, processor)

    @staticmethod
    def build_technicals_calculator() -> PipelineRunner:
        mongodb_storage = MongoDBStorage()
        symbols = AssetsProvider.get_sp500_symbols()

        from_time = datetime.now() - timedelta(days=365 * 2)
        source = MongoDBSource(mongodb_storage, symbols, TimeSpan.Day, from_time)

        sink = MongoDBSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        technical_normalizer = TechnicalsNormalizerProcessor(cache_processor)
        technicals = TechnicalsProcessor(technical_normalizer)

        return PipelineRunner(source, technicals)
