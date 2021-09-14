from typing import Optional, List, Dict

from calc.technicals import TechnicalCalculator
from entities.candle import Candle
from pipeline.processor import Processor
from pipeline.processors.candle_cache import CandleCache
from pipeline.shared_context import SharedContext

CONTEXT_IDENT = 'Technicals'
TechnicalsData = Dict[str, Dict[str, List[float]]]


class TechnicalsContextWriter:
    def __init__(self, context: SharedContext[TechnicalsData]) -> None:
        self.context = context

    def save_indicator_values(self, indicator_name: str, symbol: str, values: List[float]):
        data = self.context.get_kv_data(CONTEXT_IDENT)
        if not data:
            data = {}
            self.context.put_kv_data(CONTEXT_IDENT, data)

        if symbol not in data:
            data[symbol] = {}

        data[symbol][indicator_name] = values


class TechnicalsContextReader:
    def __init__(self, context: SharedContext[TechnicalsData]) -> None:
        self.context = context

    def get_indicator_values(self, symbol: str, indicator_name: str) -> Optional[List[float]]:
        data = self.context.get_kv_data(CONTEXT_IDENT)
        if data:
            return data.get(symbol, {}).get(indicator_name, None)


class TechnicalsProcessor(Processor):

    def __init__(self, next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)

    def process(self, context: SharedContext, candle: Candle):
        cache_reader = CandleCache.context_reader(context)
        context_writer = TechnicalsContextWriter(context)
        symbol_candles = cache_reader.get_symbol_candles(candle.symbol)
        calculator = TechnicalCalculator(symbol_candles)
        sma_values = calculator.sma(5)
        cci_values = calculator.cci(7)
        context_writer.save_indicator_values('sma5', candle.symbol, sma_values)
        context_writer.save_indicator_values('cci7', candle.symbol, cci_values)
        self.next_processor.process(context, candle)

    @staticmethod
    def context_reader(context: SharedContext[TechnicalsData]) -> TechnicalsContextReader:
        return TechnicalsContextReader(context)
