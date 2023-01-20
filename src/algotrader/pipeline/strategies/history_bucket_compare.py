import logging
from datetime import datetime
from typing import List, Dict

from algotrader.entities.candle import Candle
from algotrader.entities.strategy import Strategy
from algotrader.entities.strategy_signal import StrategySignal, SignalDirection
from algotrader.pipeline.processors.technicals_buckets_matcher import INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY, \
    IndicatorsMatchedBuckets
from algotrader.pipeline.shared_context import SharedContext
from algotrader.serialization.store import DeserializationService
from algotrader.storage.storage_provider import StorageProvider


class HistoryBucketCompareStrategy(Strategy):

    def __init__(self, storage_provider: StorageProvider, timeframe_start: datetime, timeframe_end: datetime,
                 indicators_to_compare: List[str], return_fields: List[str], min_event_count: int,
                 min_avg_return: float) -> None:
        self.timeframe_start = timeframe_start
        self.timeframe_end = timeframe_end
        self.indicators_to_compare = indicators_to_compare
        self.storage_provider = storage_provider
        self.indicators_to_compare = indicators_to_compare
        self.return_fields = return_fields
        self.min_event_count = min_event_count
        self.min_avg_return = min_avg_return

        groupby_fields = [f'attachments.indicators_matched_buckets.{ind}.ident' for ind in self.indicators_to_compare]
        return_fields = [f'attachments.returns.{return_field}' for return_field in self.return_fields]

        self.long_matchers, self.short_matchers = storage_provider.get_aggregated_history(timeframe_start,
                                                                                          timeframe_end,
                                                                                          groupby_fields,
                                                                                          return_fields,
                                                                                          min_event_count,
                                                                                          min_avg_return)

        logging.info(f'Found {len(self.long_matchers)} long matchers and {len(self.short_matchers)} short matchers')

    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        indicators_buckets: IndicatorsMatchedBuckets = \
            candle.attachments.get_attachment(INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY)

        candle_buckets_map: Dict[str, int] = {}
        for indicator in self.indicators_to_compare:
            if not indicators_buckets.has(indicator):
                return []

            candle_buckets_map[f'attachments.indicators_matched_buckets.{indicator}.ident'] = indicators_buckets.get(
                indicator).ident

        for matcher in self.long_matchers:
            match = True
            for candle_ind, candle_val in candle_buckets_map.items():
                if matcher[candle_ind] != candle_val:
                    match = False

            if match:
                return [StrategySignal(candle.symbol, SignalDirection.Long)]

        for matcher in self.short_matchers:
            match = True
            for candle_ind, candle_val in candle_buckets_map.items():
                if matcher[candle_ind] != candle_val:
                    match = False

            if match:
                return [StrategySignal(candle.symbol, SignalDirection.Short)]

        return []

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'storage_provider': self.storage_provider.serialize(),
            'timeframe_start': self.timeframe_start,
            'timeframe_end': self.timeframe_end,
            'indicators_to_compare': self.indicators_to_compare,
            'return_fields': self.return_fields,
            'min_event_count': self.min_event_count,
            'min_avg_return': self.min_avg_return,
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        storage_provider: StorageProvider = DeserializationService.deserialize(data.get('storage_provider'))

        return cls(storage_provider, data.get('timeframe_start'), data.get('timeframe_end'),
                   data.get('indicators_to_compare'), data.get('return_fields'),
                   data.get('min_event_count'), data.get('min_avg_return'))
