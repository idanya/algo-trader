from __future__ import annotations

from typing import Optional, Callable, Dict, List

from entities.candle import Candle
from entities.generic_candle_attachment import GenericCandleAttachment
from pipeline.processor import Processor
from pipeline.processors.candle_cache import CandleCache
from pipeline.processors.technicals import Indicators, INDICATORS_ATTACHMENT_KEY, IndicatorValue
from pipeline.shared_context import SharedContext

NORMALIZED_INDICATORS_ATTACHMENT_KEY = 'normalized_indicators'


class NormalizedIndicators(GenericCandleAttachment[IndicatorValue]):
    pass


NormalizedIndicators()

VWAP_NORMALIZE_PREFIXES = ['sma', 'ema']

NormalizeFunc = Callable[[List[Candle], IndicatorValue], IndicatorValue]


class TechnicalsNormalizerProcessor(Processor):
    def __init__(self, normalization_window_size: int = 3, next_processor: Optional[Processor] = None) -> None:
        super().__init__(next_processor)
        self.normalization_window_size = normalization_window_size
        self.normalizers: Dict[str, NormalizeFunc] = {}
        self._init_normalizers()

    def _init_normalizers(self):
        for prefix in VWAP_NORMALIZE_PREFIXES:
            self.normalizers[prefix] = self._normalize_vwap

    def process(self, context: SharedContext, candle: Candle):
        cache_reader = CandleCache.context_reader(context)
        symbol_candles = cache_reader.get_symbol_candles(candle.symbol) or []
        latest_candles = symbol_candles[-self.normalization_window_size:] + [candle]

        indicators: Indicators = candle.attachments.get_attachment(INDICATORS_ATTACHMENT_KEY)

        normalized_indicators = NormalizedIndicators()
        for indicator_name, indicator_value in indicators.items():
            if indicator_value:
                normalized_value = self._normalize(latest_candles, indicator_name, indicator_value)
                normalized_indicators.set(indicator_name, normalized_value)

        candle.attachments.add_attachement(NORMALIZED_INDICATORS_ATTACHMENT_KEY, normalized_indicators)

        super().process(context, candle)

    def _normalize(self, latest_candles: List[Candle], field_name: str, value: IndicatorValue) -> IndicatorValue:
        for prefix, normalizer in self.normalizers.items():
            if field_name.startswith(prefix):
                return normalizer(latest_candles, value)

        return value

    @staticmethod
    def _normalize_close(candle: Candle, value: IndicatorValue) -> IndicatorValue:
        if isinstance(value, tuple) or isinstance(value, list):
            return [v / candle.close for v in value]

        return value / candle.close

    @staticmethod
    def _normalize_vwap(latest_candles: List[Candle], value: IndicatorValue) -> IndicatorValue:
        vwap = TechnicalsNormalizerProcessor._calculate_vwap(latest_candles)
        if isinstance(value, tuple) or isinstance(value, list):
            return [v / vwap for v in value]

        return value / vwap

    @staticmethod
    def _calculate_vwap(latest_candles: List[Candle]) -> float:
        typical_prices = [(candle.close + candle.high + candle.low) / 3 for candle in latest_candles]
        volumes = [candle.volume for candle in latest_candles]
        return sum(typical_prices[i] * volumes[i] for i in range(len(typical_prices))) / sum(volumes)
