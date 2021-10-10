from datetime import datetime, timedelta

from entities.timespan import TimeSpan
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.strategy import StrategyProcessor
from pipeline.processors.technicals import TechnicalsProcessor
from pipeline.runner import PipelineRunner
from pipeline.sources.mongodb_source import MongoDBSource
from pipeline.strategies.simaple_sma import SimpleSMA
from storage.mongodb_storage import MongoDBStorage
from trade.simple_sum_signals_executor import SimpleSumSignalsExecutor


class BacktestPipelines:
    @staticmethod
    def build_mongodb_backtester() -> PipelineRunner:
        mongodb_storage = MongoDBStorage()

        from_time = datetime.now() - timedelta(days=500)
        source = MongoDBSource(mongodb_storage, ['AAPL'], TimeSpan.Day, from_time)

        cache_processor = CandleCache()
        strategy_processor = StrategyProcessor([SimpleSMA()], SimpleSumSignalsExecutor(), cache_processor)
        technicals_processor = TechnicalsProcessor(strategy_processor)
        processor = TechnicalsProcessor(technicals_processor)

        return PipelineRunner(source, processor)
