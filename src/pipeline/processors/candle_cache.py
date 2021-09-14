from typing import Optional, List, Dict

from entities.candle import Candle
from pipeline.processor import Processor
from pipeline.shared_context import SharedContext


class CandleCache(Processor):

    def __init__(self, cache_name: str, next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)
        self.cache_name = cache_name or 'CandleCache'
        self.data: Dict[str, List[Candle]] = {}

    def process(self, context: SharedContext, candle: Candle):
        if not context.get_kv_data(self.cache_name):
            context.put_kv_data(self.cache_name, self.data)

        if candle.symbol not in self.data:
            self.data[candle.symbol] = []

        self.data[candle.symbol].append(candle)

        self.next_processor.process(context, candle)
