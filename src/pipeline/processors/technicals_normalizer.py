from __future__ import annotations

from typing import Optional, Callable, Dict

from entities.candle import Candle
from entities.generic_candle_attachment import GenericCandleAttachment
from pipeline.processor import Processor
from pipeline.processors.technicals import Indicators, INDICATORS_ATTACHMENT_KEY, IndicatorValue
from pipeline.shared_context import SharedContext

NORMALIZED_INDICATORS_ATTACHMENT_KEY = 'normalized_indicators'


class NormalizedIndicators(GenericCandleAttachment[IndicatorValue]):
    pass


NormalizedIndicators()

VWAP_NORMALIZE_PREFIXES = ['sma', 'ema']

NormalizeFunc = Callable[[Candle, IndicatorValue], IndicatorValue]


class TechnicalsNormalizerProcessor(Processor):
    def __init__(self, next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)
        self.normalizers: Dict[str, NormalizeFunc] = {}
        self._init_normalizers()

    def _init_normalizers(self):
        for prefix in VWAP_NORMALIZE_PREFIXES:
            self.normalizers[prefix] = self._normalize_vwap

    def process(self, context: SharedContext, candle: Candle):
        indicators: Indicators = candle.attachments.get_attachment(INDICATORS_ATTACHMENT_KEY)
        normalized_indicators = NormalizedIndicators()
        for indicator_name, indicator_value in indicators.items():
            if indicator_value:
                normalized_value = self._normalize(candle, indicator_name, indicator_value)
                if normalized_value:
                    normalized_indicators.set(indicator_name, normalized_value)

        candle.attachments.add_attachement(NORMALIZED_INDICATORS_ATTACHMENT_KEY, normalized_indicators)

        if self.next_processor:
            self.next_processor.process(context, candle)

    def _normalize(self, candle: Candle, field_name: str, value: IndicatorValue) -> Optional[IndicatorValue]:
        for prefix, normalizer in self.normalizers.items():
            if field_name.startswith(prefix):
                return normalizer(candle, value)

    @staticmethod
    def _normalize_close(candle: Candle, value: IndicatorValue) -> IndicatorValue:
        if isinstance(value, tuple) or isinstance(value, list):
            return [v / candle.close for v in value]

        return value / candle.close

    @staticmethod
    def _normalize_vwap(candle: Candle, value: IndicatorValue) -> IndicatorValue:
        vwap = (candle.close + candle.high + candle.low) / candle.volume
        if isinstance(value, tuple) or isinstance(value, list):
            return [v / vwap for v in value]

        return value / vwap
