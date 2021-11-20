from typing import List

from entities.candle import Candle
from entities.strategy import Strategy
from entities.strategy_signal import StrategySignal, SignalDirection
from pipeline.processors.technicals_buckets_matcher import INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY, \
    IndicatorsMatchedBuckets
from pipeline.shared_context import SharedContext
from storage.storage_provider import StorageProvider


class HistoryBucketCompareStrategy(Strategy):

    def __init__(self, storage_provider: StorageProvider, indicators_to_compare: List[str], return_field: str,
                 min_event_count: int, min_avg_return: float) -> None:
        self.indicators_to_compare = indicators_to_compare

        groupby_fields = [f'attachments.indicators_matched_buckets.{ind}.ident' for ind in self.indicators_to_compare]
        return_field = f'attachments.returns.{return_field}'

        self.matchers = storage_provider.get_aggregated_history(groupby_fields, return_field,
                                                                min_event_count, min_avg_return)

    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        indicators_buckets: IndicatorsMatchedBuckets = \
            candle.attachments.get_attachment(INDICATORS_MATCHED_BUCKETS_ATTACHMENT_KEY)

        candle_buckets_map = {
            f'attachments.indicators_matched_buckets.{indicator}.ident': indicators_buckets.get(indicator).ident
            for indicator in self.indicators_to_compare}

        for matcher in self.matchers:
            for candle_ind, candle_val in candle_buckets_map.items():
                if matcher[candle_ind] != candle_val:
                    continue

            return [StrategySignal(candle.symbol, SignalDirection.Long)]
