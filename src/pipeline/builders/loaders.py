from datetime import datetime, timedelta

from entities.timespan import TimeSpan
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.mongodb_sink import MongoDBSinkProcessor
from pipeline.processors.technicals import TechnicalsProcessor
from pipeline.runner import PipelineRunner
from pipeline.sources.ib_history import IBHistorySource
from providers.ib.interactive_brokers_connector import InteractiveBrokersConnector
from storage.mongodb_storage import MongoDBStorage


class LoadersPipelines:
    @staticmethod
    def build_daily_loader() -> PipelineRunner:
        mongodb_storage = MongoDBStorage()

        from_time = datetime.now() - timedelta(days=500)
        source = IBHistorySource(InteractiveBrokersConnector(), ['AAPL'], TimeSpan.Day, from_time)

        sink = MongoDBSinkProcessor(mongodb_storage)
        cache_processor = CandleCache(sink)
        processor = TechnicalsProcessor(cache_processor)

        return PipelineRunner(source, processor)
