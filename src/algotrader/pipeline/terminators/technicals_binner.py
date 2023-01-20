from __future__ import annotations

import json
import math
from typing import List, Dict, Tuple

from algotrader.entities.bucket import Bucket
from algotrader.entities.bucketscontainer import BucketsContainer
from algotrader.entities.candle import Candle
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.processors.technicals import IndicatorValue
from algotrader.pipeline.processors.technicals_normalizer import NormalizedIndicators, \
    NORMALIZED_INDICATORS_ATTACHMENT_KEY
from algotrader.pipeline.shared_context import SharedContext
from algotrader.pipeline.terminator import Terminator


class TechnicalsBinner(Terminator):
    def __init__(self, symbols: List[str], bins_count: int, output_file_path: str,
                 outliers_removal_percentage: float = 0.05) -> None:
        super().__init__()
        self.outliers_removal_percentage = outliers_removal_percentage
        self.symbols = symbols
        self.output_file_path = output_file_path
        self.values: Dict[str, List[IndicatorValue]] = {}
        self.bins = BucketsContainer()
        self.bins_count = bins_count

    def terminate(self, context: SharedContext):
        cache_reader = CandleCache.context_reader(context)

        for symbol in self.symbols:
            symbol_candles = cache_reader.get_symbol_candles(symbol) or []
            for candle in symbol_candles:
                self._process_candle(candle)

        self._calculate_bins()
        self._save_bins()

    def _process_candle(self, candle: Candle):
        normalized_indicators: NormalizedIndicators = candle.attachments.get_attachment(
            NORMALIZED_INDICATORS_ATTACHMENT_KEY)

        if not normalized_indicators:
            return

        for indicator, value in normalized_indicators.items():
            if indicator not in self.values:
                self.values[indicator] = []

            self.values[indicator].append(value)

    def _calculate_bins(self):
        for indicator, values in self.values.items():
            if isinstance(values[0], float):
                self.bins.add(indicator, self._get_single_float_bins(values))
            elif isinstance(values[0], list) or isinstance(values[0], Tuple):
                list_size = len(values[0])
                bins: List[List[Bucket]] = []
                for i in range(list_size):
                    bins.append(self._get_single_float_bins([v[i] for v in values]))

                self.bins.add(indicator, bins)

    def _get_single_float_bins(self, values: List[float]) -> List[Bucket]:
        values.sort()

        margins = int(len(values) * self.outliers_removal_percentage)
        values = values[margins:len(values) - margins]

        step_size = int(math.floor(len(values) / self.bins_count))

        bins: List[Bucket] = [Bucket(ident=0, end=values[0])]

        for i in range(0, len(values), step_size):
            bins.append(Bucket(ident=len(bins), start=values[i], end=values[min(i + step_size, len(values) - 1)]))

        bins.append(Bucket(ident=len(bins), start=values[len(values) - 1]))

        return bins

    def _save_bins(self):
        with open(self.output_file_path, 'w+') as output_file:
            output_file.write(json.dumps(self.bins.serialize()))

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'symbols': self.symbols,
            'bins_count': self.bins_count,
            'output_file_path': self.output_file_path,
            'outliers_removal_percentage': self.outliers_removal_percentage
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        return cls(data.get('symbols'), data.get('bins_count'), data.get('output_file_path'),
                   data.get('outliers_removal_percentage'))
