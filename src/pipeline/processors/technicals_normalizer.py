from __future__ import annotations

from typing import Optional

from entities.candle import Candle
from entities.generic_candle_attachment import GenericCandleAttachment
from pipeline.processor import Processor
from pipeline.processors.technicals import Indicators, INDICATORS_ATTACHMENT_KEY, IndicatorValue
from pipeline.shared_context import SharedContext

NORMALIZED_INDICATORS_ATTACHMENT_KEY = 'normalized_indicators'


class NormalizedIndicators(GenericCandleAttachment[IndicatorValue]):
    pass


NormalizedIndicators()

CLOSE_NORMALIZE_PREFIXES = ['sma', 'ema']


class TechnicalsNormalizerProcessor(Processor):
    def __init__(self, next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)

    def process(self, context: SharedContext, candle: Candle):
        indicators: Indicators = candle.attachments.get_attachment(INDICATORS_ATTACHMENT_KEY)
        normalized_indicators = NormalizedIndicators()
        for k, v in indicators.items():
            if v and self._is_close_normalized(k):
                normalized_indicators.set(k, self._normalize(candle, v))

        candle.attachments.add_attachement(NORMALIZED_INDICATORS_ATTACHMENT_KEY, normalized_indicators)

        if self.next_processor:
            self.next_processor.process(context, candle)

    @staticmethod
    def _is_close_normalized(field_name: str):
        return any(prefix for prefix in CLOSE_NORMALIZE_PREFIXES if field_name.startswith(prefix))

    @staticmethod
    def _normalize(candle: Candle, value: IndicatorValue) -> IndicatorValue:
        if isinstance(value, tuple) or isinstance(value, list):
            return [v / candle.close for v in value]

        return value / candle.close
