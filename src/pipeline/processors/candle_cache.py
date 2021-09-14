from typing import Optional, List, Dict

from entities.candle import Candle
from pipeline.processor import Processor
from pipeline.shared_context import SharedContext

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


class CandleCache(Processor):
    def __init__(self, next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)
        self.data: CacheData = {}

    def process(self, context: SharedContext, candle: Candle):
        context_writer = CandleCacheContextWriter(context)
        context_writer.put_candle(candle)
        self.next_processor.process(context, candle)

    @staticmethod
    def context_reader(context: SharedContext) -> CandleCacheContextReader:
        return CandleCacheContextReader(context)
