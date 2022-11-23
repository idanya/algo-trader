from datetime import datetime
from typing import List

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
        last_symbol_timestamp = datetime.now()
        for symbol in self.symbols:
            last_candle_timestamp = cache_reader.get_symbol_candles(symbol)[-1].timestamp
            if last_symbol_timestamp > last_candle_timestamp: last_symbol_timestamp = last_candle_timestamp

        context.put_kv_data(CONTEXT_IDENT, last_symbol_timestamp)

    @staticmethod
    def get(context: SharedContext):
        return context.get_kv_data(CONTEXT_IDENT, datetime.now())
