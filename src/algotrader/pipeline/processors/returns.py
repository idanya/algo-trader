from __future__ import annotations

from typing import List, Dict, Optional

from algotrader.entities.candle import Candle
from algotrader.entities.generic_candle_attachment import GenericCandleAttachment
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.shared_context import SharedContext

RETURNS_ATTACHMENT_KEY = 'returns'


class Returns(GenericCandleAttachment[float]):
    pass


Returns()


class ReturnsCalculatorProcessor(Processor):
    def __init__(self, field_prefix: str, returns_count: int, next_processor: Optional[Processor] = None):
        super().__init__(next_processor)
        self.field_prefix = field_prefix
        self.returns_count = returns_count

    def process(self, context: SharedContext, candle: Candle):
        cache_reader = CandleCache.context_reader(context)
        symbol_candles = cache_reader.get_symbol_candles(candle.symbol) or []

        candle.attachments.add_attachement(RETURNS_ATTACHMENT_KEY, Returns())

        if len(symbol_candles) >= self.returns_count:
            candle_returns = self._calc_returns(candle, symbol_candles)
            candle.attachments.add_attachement(RETURNS_ATTACHMENT_KEY, candle_returns)

        if self.next_processor:
            self.next_processor.process(context, candle)

    def _calc_returns(self, current_candle: Candle, candles: List[Candle]) -> Returns:
        candle_returns = Returns()
        for i in range(1, self.returns_count + 1):
            candle_returns.set(f'{self.field_prefix}-{i}', (1 - current_candle.close / candles[-i].close) * 100)

        return candle_returns

    def serialize(self) -> Dict:
        return {
            'returnsCount': self.returns_count,
            'fieldPrefix': self.field_prefix
        }

    @classmethod
    def deserialize(cls, data: Dict) -> Optional[Processor]:
        return cls(data['fieldPrefix'], data['returnsCount'], cls._deserialize_next_processor(data))
