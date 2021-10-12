from __future__ import annotations

from typing import Dict, List

from entities.candle import Candle
from entities.serializable import Serializable, Deserializable
from pipeline.processor import Processor
from pipeline.processors.candle_cache import CandleCache
from pipeline.shared_context import SharedContext

RETURNS_ATTACHMENT_KEY = 'returns'


class Returns(Serializable, Deserializable):
    def __init__(self) -> None:
        super().__init__()
        self.returns: Dict[str, float] = {}

    def __getitem__(self, key):
        return self.returns[key]

    @classmethod
    def deserialize(cls, data: Dict) -> Returns:
        obj = Returns()
        obj.returns = data
        return obj

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update(self.returns)
        return obj

    def has(self, key: str):
        return key in self.returns and self.returns[key] is not None


class ReturnsCalculatorProcessor(Processor):
    def process(self, context: SharedContext, candle: Candle):
        cache_reader = CandleCache.context_reader(context)
        symbol_candles = cache_reader.get_symbol_candles(candle.symbol) or []

        if len(symbol_candles) > 5:
            candle_returns = self._calc_returns(candle, symbol_candles)
            candle.attachments.add_attachement(RETURNS_ATTACHMENT_KEY, candle_returns)

        if self.next_processor:
            self.next_processor.process(context, candle)

    @staticmethod
    def _calc_returns(current_candle: Candle, candles: List[Candle]) -> Returns:
        candle_returns = Returns()
        for i in range(1, 5):
            candle_returns.returns[f'ctc{i}'] = (1 - current_candle.close / candles[-i].close) * 100

        return candle_returns
