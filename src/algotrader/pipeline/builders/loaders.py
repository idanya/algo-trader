from datetime import datetime, timedelta
from typing import Optional

from assets.assets_provider import AssetsProvider

from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.builders import TECHNICAL_PROCESSOR_CONFIG
from algotrader.pipeline.pipeline import Pipeline
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.processors.assets_correlation import AssetCorrelationProcessor
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.processors.returns import ReturnsCalculatorProcessor
from algotrader.pipeline.processors.storage_provider_sink import StorageSinkProcessor
from algotrader.pipeline.processors.technicals import TechnicalsProcessor
from algotrader.pipeline.processors.technicals_buckets_matcher import TechnicalsBucketsMatcher
from algotrader.pipeline.processors.technicals_normalizer import TechnicalsNormalizerProcessor
from algotrader.pipeline.processors.timespan_change import TimeSpanChangeProcessor
from algotrader.pipeline.reverse_source import ReverseSource
from algotrader.pipeline.source import Source
from algotrader.pipeline.sources.binance_history import BinanceHistorySource
from algotrader.pipeline.sources.binance_realtime import BinanceRealtimeSource
from algotrader.pipeline.sources.ib_history import IBHistorySource
from algotrader.pipeline.sources.mongodb_source import MongoDBSource
from algotrader.pipeline.sources.yahoo_finance_history import YahooFinanceHistorySource
from algotrader.pipeline.terminators.technicals_binner import TechnicalsBinner
from algotrader.providers.binance import BinanceProvider
from algotrader.providers.ib.interactive_brokers_connector import InteractiveBrokersConnector
from algotrader.storage.mongodb_storage import MongoDBStorage

DEFAULT_DAYS_BACK = 365 * 1
STATIC_NOW = datetime(2022, 1, 1)


class LoadersPipelines:
    @staticmethod
    def build_daily_ib_loader(days_back: int = DEFAULT_DAYS_BACK) -> Pipeline:
        mongodb_storage = MongoDBStorage()

        from_time = STATIC_NOW - timedelta(days=days_back)
        symbols = AssetsProvider.get_sp500_symbols()

        source = IBHistorySource(InteractiveBrokersConnector(), symbols, TimeSpan.Day, from_time)

        sink = StorageSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = TechnicalsProcessor(TECHNICAL_PROCESSOR_CONFIG, cache_processor)

        return Pipeline(source, processor)

    @staticmethod
    def build_daily_yahoo_loader(days_back: int = DEFAULT_DAYS_BACK) -> Pipeline:
        mongodb_storage = MongoDBStorage()

        from_time = STATIC_NOW - timedelta(days=days_back)
        symbols = AssetsProvider.get_sp500_symbols()

        source = YahooFinanceHistorySource(symbols, TimeSpan.Day, from_time, STATIC_NOW)

        sink = StorageSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = TechnicalsProcessor(TECHNICAL_PROCESSOR_CONFIG, cache_processor)

        return Pipeline(source, processor)

    @staticmethod
    def build_daily_binance_loader(days_back: int = DEFAULT_DAYS_BACK) -> Pipeline:
        mongodb_storage = MongoDBStorage()

        from_time = STATIC_NOW - timedelta(days=days_back)
        symbols = AssetsProvider.get_crypto_symbols()

        provider = BinanceProvider(enable_websocket=False)
        source = BinanceHistorySource(provider, symbols, TimeSpan.Day, from_time, STATIC_NOW)

        sink = StorageSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = TechnicalsProcessor(TECHNICAL_PROCESSOR_CONFIG, cache_processor)

        return Pipeline(source, processor)

    @staticmethod
    def build_realtime_binance() -> Pipeline:
        mongodb_storage = MongoDBStorage()

        symbols = AssetsProvider.get_crypto_symbols()

        provider = BinanceProvider(enable_websocket=True)
        source = BinanceRealtimeSource(provider, symbols, TimeSpan.Second)

        sink = StorageSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = TechnicalsProcessor(TECHNICAL_PROCESSOR_CONFIG, cache_processor)

        return Pipeline(source, processor)

    @staticmethod
    def build_returns_calculator(days_back: int = DEFAULT_DAYS_BACK) -> Pipeline:
        mongodb_storage = MongoDBStorage()
        symbols = AssetsProvider.get_sp500_symbols()

        from_time = STATIC_NOW - timedelta(days=days_back)
        source = MongoDBSource(mongodb_storage, symbols, TimeSpan.Day, from_time, STATIC_NOW)
        source = ReverseSource(source)

        sink = StorageSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = ReturnsCalculatorProcessor('ctc', 5, cache_processor)

        return Pipeline(source, processor)

    @staticmethod
    def _build_mongo_source(days_back: int) -> Source:
        mongodb_storage = MongoDBStorage()
        symbols = AssetsProvider.get_sp500_symbols()

        from_time = STATIC_NOW - timedelta(days=days_back)
        source = MongoDBSource(mongodb_storage, symbols, TimeSpan.Day, from_time, STATIC_NOW)
        return source

    @staticmethod
    def _build_technicals_base_processor_chain(bins_file_path: Optional[str] = None,
                                               correlations_file_path: Optional[str] = None) -> Processor:
        mongodb_storage = MongoDBStorage()
        sink = StorageSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)

        latest_processor = cache_processor

        if bins_file_path:
            bucket_matcher = TechnicalsBucketsMatcher(bins_file_path, next_processor=latest_processor)
            latest_processor = bucket_matcher

        if correlations_file_path:
            asset_correlation = AssetCorrelationProcessor(correlations_file_path, next_processor=latest_processor)
            latest_processor = asset_correlation

        technical_normalizer = TechnicalsNormalizerProcessor(next_processor=latest_processor)
        technicals = TechnicalsProcessor(TECHNICAL_PROCESSOR_CONFIG, technical_normalizer)
        timespan_change_processor = TimeSpanChangeProcessor(TimeSpan.Day, technicals)
        return timespan_change_processor

    @staticmethod
    def build_technicals_calculator(days_back: int = DEFAULT_DAYS_BACK) -> Pipeline:
        source = LoadersPipelines._build_mongo_source(days_back)
        technicals = LoadersPipelines._build_technicals_base_processor_chain()
        return Pipeline(source, technicals)

    @staticmethod
    def build_technicals_with_buckets_calculator(bins_file_path: str, bins_count: int,
                                                 correlations_file_path: str,
                                                 days_back: int = DEFAULT_DAYS_BACK) -> Pipeline:
        source = LoadersPipelines._build_mongo_source(days_back)
        technicals = LoadersPipelines._build_technicals_base_processor_chain(
            correlations_file_path=correlations_file_path)

        symbols = AssetsProvider.get_sp500_symbols()
        technicals_binner = TechnicalsBinner(symbols, bins_count, bins_file_path)

        return Pipeline(source, technicals, technicals_binner)

    @staticmethod
    def build_technicals_with_buckets_matcher(bins_file_path: str,
                                              correlations_file_path: str,
                                              days_back: int = DEFAULT_DAYS_BACK) -> Pipeline:
        source = LoadersPipelines._build_mongo_source(days_back)

        technicals = LoadersPipelines._build_technicals_base_processor_chain(bins_file_path, correlations_file_path)

        return Pipeline(source, technicals)
