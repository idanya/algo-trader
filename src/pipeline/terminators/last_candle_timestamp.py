from datetime import datetime
from typing import List
from entities.candle import Candle
from entities.timespan import TimeSpan

from pipeline.processors.candle_cache import CandleCache
from pipeline.shared_context import SharedContext
from pipeline.terminator import Terminator

CONTEXT_IDENT = 'LastSymbolTimestamp'


class LastSymbolTimestamp(Terminator):
    def __init__(self, symbols: List[str]) -> None:
        super().__init__()
        self.symbols = symbols

    def terminate(self, context: SharedContext):
        cache_reader = CandleCache.context_reader(context)
        now = datetime.now()
        last_symbol_timestamp = now
        for symbol in self.symbols:
            symbol_candles = cache_reader.get_symbol_candles(symbol) or [Candle(symbol, TimeSpan.Minute, now, 0, 0, 0, 0, 0)]
            last_candle_timestamp = symbol_candles[-1].timestamp
            if last_symbol_timestamp > last_candle_timestamp:
                last_symbol_timestamp = last_candle_timestamp

        context.put_kv_data(CONTEXT_IDENT, last_symbol_timestamp)

    @staticmethod
    def get(context: SharedContext):
        return context.get_kv_data(CONTEXT_IDENT, datetime.now())
