import random
from datetime import datetime, timedelta
from typing import List
from unittest import TestCase

import mongomock

from algotrader.entities.bucket import Bucket
from algotrader.entities.candle import Candle
from algotrader.entities.strategy_signal import StrategySignal, SignalDirection
from algotrader.entities.timespan import TimeSpan
from fakes.strategy_executor import FakeSignalsExecutor
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.processors.returns import Returns, RETURNS_ATTACHMENT_KEY
from algotrader.pipeline.processors.strategy import StrategyProcessor
from algotrader.pipeline.processors.technicals_buckets_matcher import IndicatorsMatchedBuckets, \
    INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY
from algotrader.pipeline.shared_context import SharedContext
from algotrader.pipeline.strategies.history_bucket_compare import HistoryBucketCompareStrategy
from algotrader.storage.mongodb_storage import MongoDBStorage
from unit import TEST_SYMBOL, generate_candle


class TestHistoryCompareStrategy(TestCase):
    @mongomock.patch(servers=(('localhost', 27017),))
    def test_long(self):
        def _check(signals: List[StrategySignal]):
            self.assertEqual(1, len(signals))
            self.assertEqual(TEST_SYMBOL, signals[0].symbol)
            self.assertEqual(SignalDirection.Long, signals[0].direction)

        candle = self._get_candle()

        context = SharedContext()
        cache_processor = CandleCache(None)
        cache_processor.process(context, candle)

        mongodb_storage = MongoDBStorage()
        mongodb_storage.__drop_collections__()

        mongodb_storage.save(self._get_history_candle(0.5))

        history_compare_strategy = HistoryBucketCompareStrategy(mongodb_storage,
                                                                datetime.now() - timedelta(days=60),
                                                                datetime.now(),
                                                                indicators_to_compare=['sma5', 'sma20'],
                                                                return_fields=['ctc1'], min_event_count=1,
                                                                min_avg_return=0.2)

        # TODO: FakeSignalsExecutor is not called when there is not signal. make sure to fail if it's not called.
        processor = StrategyProcessor([history_compare_strategy], FakeSignalsExecutor(_check), None)
        processor.process(context, candle)

    @mongomock.patch(servers=(('localhost', 27017),))
    def test_no_signals(self):
        def _check(signals: List[StrategySignal]):
            if signals:
                self.fail()

        candle = self._get_candle()

        context = SharedContext()
        cache_processor = CandleCache(None)
        cache_processor.process(context, candle)

        mongodb_storage = MongoDBStorage()
        mongodb_storage.__drop_collections__()

        mongodb_storage.save(self._get_history_candle(0.15))

        history_compare_strategy = HistoryBucketCompareStrategy(mongodb_storage,
                                                                datetime.now() - timedelta(days=60),
                                                                datetime.now(),
                                                                indicators_to_compare=['sma5', 'sma20'],
                                                                return_fields=['ctc1'], min_event_count=1,
                                                                min_avg_return=0.2)

        # TODO: FakeSignalsExecutor is not called when there is not signal. make sure to fail if it's not called.
        processor = StrategyProcessor([history_compare_strategy], FakeSignalsExecutor(_check), None)
        processor.process(context, candle)

    @mongomock.patch(servers=(('localhost', 27017),))
    def test_no_signal_because_timeframe(self):
        def _check(signals: List[StrategySignal]):
            if signals:
                self.fail()

        candle = self._get_candle()

        context = SharedContext()
        cache_processor = CandleCache(None)
        cache_processor.process(context, candle)

        mongodb_storage = MongoDBStorage()
        mongodb_storage.__drop_collections__()

        mongodb_storage.save(self._get_history_candle(0.5))

        history_compare_strategy = HistoryBucketCompareStrategy(mongodb_storage,
                                                                datetime.now(),
                                                                datetime.now(),
                                                                indicators_to_compare=['sma5', 'sma20'],
                                                                return_fields=['ctc1'], min_event_count=1,
                                                                min_avg_return=0.2)

        # TODO: FakeSignalsExecutor is not called when there is not signal. make sure to fail if it's not called.
        processor = StrategyProcessor([history_compare_strategy], FakeSignalsExecutor(_check), None)
        processor.process(context, candle)

    def _get_history_candle(self, ctc_value: float) -> Candle:
        candle = generate_candle(TimeSpan.Day, datetime.now() - timedelta(days=random.randint(2, 50)))

        indicator_buckets = IndicatorsMatchedBuckets()
        indicator_buckets.set('sma5', Bucket(ident=0, start=0, end=0))
        indicator_buckets.set('sma20', Bucket(ident=4, start=7, end=9))

        candle_returns = Returns()
        candle_returns.set('ctc1', ctc_value)

        candle.attachments.add_attachement(INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY, indicator_buckets)
        candle.attachments.add_attachement(RETURNS_ATTACHMENT_KEY, candle_returns)

        return candle

    def _get_candle(self) -> Candle:
        candle = generate_candle(TimeSpan.Day, datetime.now())

        indicator_buckets = IndicatorsMatchedBuckets()
        indicator_buckets.set('sma5', Bucket(ident=0, start=0, end=0))
        indicator_buckets.set('sma20', Bucket(ident=4, start=7, end=9))

        candle.attachments.add_attachement(INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY, indicator_buckets)
        return candle
