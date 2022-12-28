from datetime import datetime
from typing import List, Dict

from entities.candle import Candle
from entities.strategy import Strategy
from entities.strategy_signal import StrategySignal, SignalDirection
from pipeline.processors.technicals_buckets_matcher import INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY, \
    IndicatorsMatchedBuckets
from pipeline.shared_context import SharedContext
from serialization.store import DeserializationService
from storage.storage_provider import StorageProvider


class HistoryBucketCompareStrategy(Strategy):

    def __init__(self, storage_provider: StorageProvider, timeframe_start: datetime, timeframe_end: datetime,
                 indicators_to_compare: List[str], return_field: str, min_event_count: int,
                 min_avg_return: float) -> None:
        self.timeframe_start = timeframe_start
        self.timeframe_end = timeframe_end
        self.indicators_to_compare = indicators_to_compare
        self.storage_provider = storage_provider
        self.indicators_to_compare = indicators_to_compare
        self.return_field = return_field
        self.min_event_count = min_event_count
        self.min_avg_return = min_avg_return

        groupby_fields = [f'attachments.indicators_matched_buckets.{ind}.ident' for ind in self.indicators_to_compare]
        return_field = f'attachments.returns.{return_field}'

        self.matchers = storage_provider.get_aggregated_history(timeframe_start, timeframe_end, groupby_fields,
                                                                return_field, min_event_count, min_avg_return)

    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        indicators_buckets: IndicatorsMatchedBuckets = \
            candle.attachments.get_attachment(INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY)

        candle_buckets_map: Dict[str, int] = {}
        for indicator in self.indicators_to_compare:
            if not indicators_buckets.has(indicator):
                return []

            candle_buckets_map[f'attachments.indicators_matched_buckets.{indicator}.ident'] = indicators_buckets.get(
                indicator).ident

        for matcher in self.matchers:
            match = True
            for candle_ind, candle_val in candle_buckets_map.items():
                if matcher[candle_ind] != candle_val:
                    match = False

            if match:
                return [StrategySignal(candle.symbol, SignalDirection.Long)]

        return []

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'storage_provider': self.storage_provider.serialize(),
            'timeframe_start': self.timeframe_start,
            'timeframe_end': self.timeframe_end,
            'indicators_to_compare': self.indicators_to_compare,
            'return_field': self.return_field,
            'min_event_count': self.min_event_count,
            'min_avg_return': self.min_avg_return,
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        storage_provider: StorageProvider = DeserializationService.deserialize(data.get('storage_provider'))

        return cls(storage_provider, data.get('timeframe_start'), data.get('timeframe_end'),
                   data.get('indicators_to_compare'), data.get('return_field'),
                   data.get('min_event_count'), data.get('min_avg_return'))
