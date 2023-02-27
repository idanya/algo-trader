from datetime import datetime, timedelta

from algotrader.assets.assets_provider import AssetsProvider
from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.builders import TECHNICAL_PROCESSOR_CONFIG
from algotrader.pipeline.pipeline import Pipeline
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.processors.strategy import StrategyProcessor
from algotrader.pipeline.processors.technicals import TechnicalsProcessor
from algotrader.pipeline.processors.technicals_buckets_matcher import TechnicalsBucketsMatcher
from algotrader.pipeline.processors.technicals_normalizer import TechnicalsNormalizerProcessor
from algotrader.pipeline.sources.mongodb_source import MongoDBSource
from algotrader.pipeline.strategies.connors_rsi2 import ConnorsRSI2
from algotrader.pipeline.strategies.history_bucket_compare import HistoryBucketCompareStrategy
from algotrader.pipeline.strategies.history_cosine_similarity import HistoryCosineSimilarityStrategy
from algotrader.storage.mongodb_storage import MongoDBStorage
from algotrader.trade.simple_sum_signals_executor import SimpleSumSignalsExecutor

STATIC_NOW = datetime(2022, 1, 1)


class BacktestPipelines:
    @staticmethod
    def build_mongodb_backtester() -> Pipeline:
        mongodb_storage = MongoDBStorage()
        symbols = AssetsProvider.get_sp500_symbols()

        from_time = STATIC_NOW - timedelta(days=365 * 2)
        source = MongoDBSource(mongodb_storage, symbols, TimeSpan.Day, from_time, STATIC_NOW)

        cache_processor = CandleCache()
        strategy_processor = StrategyProcessor([ConnorsRSI2()], SimpleSumSignalsExecutor(), cache_processor)
        technicals_processor = TechnicalsProcessor(TECHNICAL_PROCESSOR_CONFIG, strategy_processor)

        return Pipeline(source, technicals_processor)

    @staticmethod
    def build_mongodb_history_buckets_backtester(bins_file_path: str) -> Pipeline:
        mongodb_storage = MongoDBStorage()
        symbols = AssetsProvider.get_sp500_symbols()

        backtest_from_time = STATIC_NOW - timedelta(days=30 * 6)
        data_from_time = STATIC_NOW - timedelta(days=365 * 3)
        source = MongoDBSource(mongodb_storage, symbols, TimeSpan.Day, backtest_from_time, STATIC_NOW)

        return_fields = [f'ctc-{i}' for i in range(1, 10)]

        history_compare_strategy = HistoryBucketCompareStrategy(mongodb_storage,
                                                                data_from_time,
                                                                backtest_from_time,
                                                                indicators_to_compare=['sma5', 'sma20',
                                                                                       'cci7', 'cci14',
                                                                                       'rsi7', 'rsi14',
                                                                                       'stddev5', 'ema5',
                                                                                       'ema20', 'correlation'],
                                                                return_fields=return_fields, min_event_count=50,
                                                                min_avg_return=0.2)

        cache_processor = CandleCache()
        strategy_processor = StrategyProcessor([history_compare_strategy], SimpleSumSignalsExecutor(), cache_processor)
        bucket_matcher = TechnicalsBucketsMatcher(bins_file_path, next_processor=strategy_processor)
        technical_normalizer = TechnicalsNormalizerProcessor(next_processor=bucket_matcher)
        processor = TechnicalsProcessor(TECHNICAL_PROCESSOR_CONFIG, technical_normalizer)

        return Pipeline(source, processor)

    @staticmethod
    def build_mongodb_history_similarity_backtester(bins_file_path: str) -> Pipeline:
        mongodb_storage = MongoDBStorage()
        symbols = AssetsProvider.get_sp500_symbols()

        backtest_from_time = STATIC_NOW - timedelta(days=30 * 6)
        data_from_time = STATIC_NOW - timedelta(days=365 * 3)
        source = MongoDBSource(mongodb_storage, symbols, TimeSpan.Day, backtest_from_time, STATIC_NOW)

        history_compare_strategy = HistoryCosineSimilarityStrategy(mongodb_storage,
                                                                   data_from_time,
                                                                   backtest_from_time,
                                                                   indicators_to_compare=['sma5', 'sma20',
                                                                                          'cci7', 'cci14',
                                                                                          'rsi2', 'rsi7',
                                                                                          'stddev5', 'ema5', 'ema20'],
                                                                   return_field='ctc1', min_event_count=50,
                                                                   min_avg_return=0.3)

        cache_processor = CandleCache()
        strategy_processor = StrategyProcessor([history_compare_strategy], SimpleSumSignalsExecutor(), cache_processor)
        bucket_matcher = TechnicalsBucketsMatcher(bins_file_path, next_processor=strategy_processor)
        technical_normalizer = TechnicalsNormalizerProcessor(next_processor=bucket_matcher)
        processor = TechnicalsProcessor(TECHNICAL_PROCESSOR_CONFIG, technical_normalizer)

        return Pipeline(source, processor)
