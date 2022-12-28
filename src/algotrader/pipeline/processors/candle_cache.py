from typing import Optional, List, Dict

from algotrader.entities.candle import Candle
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.shared_context import SharedContext

CONTEXT_IDENT = 'CandleCache'
CacheData = Dict[str, List[Candle]]


class CandleCacheContextWriter:
    def __init__(self, context: SharedContext[CacheData]) -> None:
        super().__init__()
        self.context = context
        self.data: CacheData = {}

    def put_candle(self, candle: Candle):
        if not self.context.get_kv_data(CONTEXT_IDENT):
            self.context.put_kv_data(CONTEXT_IDENT, {})

        self.data = self.context.get_kv_data(CONTEXT_IDENT)

        if candle.symbol not in self.data:
            self.data[candle.symbol] = []

        self.data[candle.symbol].append(candle)


class CandleCacheContextReader:
    def __init__(self, context: SharedContext[CacheData]) -> None:
        super().__init__()
        self.context = context

    def get_symbol_candles(self, symbol: str) -> Optional[List[Candle]]:
        data = self.context.get_kv_data(CONTEXT_IDENT)
        if data and symbol in data:
            return data[symbol]

    def get_symbols_list(self) -> Optional[List[str]]:
        data = self.context.get_kv_data(CONTEXT_IDENT)
        if data:
            return list(data.keys())


class CandleCache(Processor):
    """
    Provides a cache facade for processed candles
    """
    def __init__(self, next_processor: Optional[Processor] = None) -> None:
        super().__init__(next_processor)
        self.data: CacheData = {}

    def reprocess(self, context: SharedContext, candle: Candle):
        context_reader = CandleCacheContextReader(context)
        candles = context_reader.get_symbol_candles(candle.symbol)

        for i in range(len(candles)):
            if candles[i].timestamp == candle.timestamp:
                candles[i] = candle
                break

        super().reprocess(context, candle)

    def process(self, context: SharedContext, candle: Candle):
        context_writer = CandleCacheContextWriter(context)
        context_writer.put_candle(candle)

        super().process(context, candle)

    @staticmethod
    def context_reader(context: SharedContext) -> CandleCacheContextReader:
        return CandleCacheContextReader(context)
