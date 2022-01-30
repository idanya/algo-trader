from datetime import datetime, timedelta
from typing import Optional

from assets.assets_provider import AssetsProvider
from entities.timespan import TimeSpan
from pipeline.processor import Processor
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.mongodb_sink import MongoDBSinkProcessor
from pipeline.processors.returns import ReturnsCalculatorProcessor
from pipeline.processors.technicals import TechnicalsProcessor
from pipeline.processors.technicals_buckets_matcher import TechnicalsBucketsMatcher
from pipeline.processors.technicals_normalizer import TechnicalsNormalizerProcessor
from pipeline.reverse_source import ReverseSource
from pipeline.runner import PipelineRunner
from pipeline.source import Source
from pipeline.sources.ib_history import IBHistorySource
from pipeline.sources.mongodb_source import MongoDBSource
from pipeline.terminators.technicals_binner import TechnicalsBinner
from providers.ib.interactive_brokers_connector import InteractiveBrokersConnector
from storage.mongodb_storage import MongoDBStorage

DEFAULT_DAYS_BACK = 365 * 3


class LoadersPipelines:
    @staticmethod
    def build_daily_loader(days_back: int = DEFAULT_DAYS_BACK) -> PipelineRunner:
        mongodb_storage = MongoDBStorage()

        from_time = datetime.now() - timedelta(days=days_back)
        symbols = AssetsProvider.get_sp500_symbols()

        source = IBHistorySource(InteractiveBrokersConnector(), symbols, TimeSpan.Day, from_time)

        sink = MongoDBSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = TechnicalsProcessor(cache_processor)

        return PipelineRunner(source, processor)

    @staticmethod
    def build_returns_calculator(days_back: int = DEFAULT_DAYS_BACK) -> PipelineRunner:
        mongodb_storage = MongoDBStorage()
        symbols = AssetsProvider.get_sp500_symbols()

        from_time = datetime.now() - timedelta(days=days_back)
        source = MongoDBSource(mongodb_storage, symbols, TimeSpan.Day, from_time)
        source = ReverseSource(source)

        sink = MongoDBSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = ReturnsCalculatorProcessor(cache_processor)

        return PipelineRunner(source, processor)

    @staticmethod
    def _build_mongo_source(days_back: int) -> Source:
        mongodb_storage = MongoDBStorage()
        symbols = AssetsProvider.get_sp500_symbols()

        from_time = datetime.now() - timedelta(days=days_back)
        source = MongoDBSource(mongodb_storage, symbols, TimeSpan.Day, from_time)
        return source

    @staticmethod
    def _build_technicals_base_processor_chain(bins_file_path: Optional[str] = None) -> Processor:
        mongodb_storage = MongoDBStorage()
        sink = MongoDBSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)

        bucket_matcher: Optional[TechnicalsBucketsMatcher] = None
        if bins_file_path:
            bucket_matcher = TechnicalsBucketsMatcher(bins_file_path, next_processor=cache_processor)

        technical_normalizer = TechnicalsNormalizerProcessor(
            next_processor=bucket_matcher if bins_file_path else cache_processor)
        technicals = TechnicalsProcessor(technical_normalizer)
        return technicals

    @staticmethod
    def build_technicals_calculator(days_back: int = DEFAULT_DAYS_BACK) -> PipelineRunner:
        source = LoadersPipelines._build_mongo_source(days_back)
        technicals = LoadersPipelines._build_technicals_base_processor_chain()
        return PipelineRunner(source, technicals)

    @staticmethod
    def build_technicals_with_buckets_calculator(bins_file_path: str, bins_count: int,
                                                 days_back: int = DEFAULT_DAYS_BACK) -> PipelineRunner:
        source = LoadersPipelines._build_mongo_source(days_back)
        technicals = LoadersPipelines._build_technicals_base_processor_chain()

        symbols = AssetsProvider.get_sp500_symbols()
        technicals_binner = TechnicalsBinner(symbols, bins_count, bins_file_path)

        return PipelineRunner(source, technicals, technicals_binner)

    @staticmethod
    def build_technicals_with_buckets_matcher(bins_file_path: str,
                                              days_back: int = DEFAULT_DAYS_BACK) -> PipelineRunner:
        source = LoadersPipelines._build_mongo_source(days_back)

        technicals = LoadersPipelines._build_technicals_base_processor_chain(bins_file_path)

        return PipelineRunner(source, technicals)
