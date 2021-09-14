from typing import Optional, List, Dict, Union

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

    def save_indicator_values(self, indicator_name: str, symbol: str, values: Union[List[List[float]], List[float]]):
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

    def get_indicator_values(self, symbol: str, indicator_name: str) -> Optional[Union[List[List[float]], List[float]]]:
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

        self._calculate(context_writer, candle.symbol, calculator)
        self.next_processor.process(context, candle)

    def _calculate(self, context_writer: TechnicalsContextWriter, symbol: str, calculator: TechnicalCalculator):
        context_writer.save_indicator_values('sma5', symbol, calculator.sma(5))
        context_writer.save_indicator_values('cci7', symbol, calculator.cci(7))
        context_writer.save_indicator_values('macd', symbol, calculator.macd(2, 5, 9))

    @staticmethod
    def context_reader(context: SharedContext[TechnicalsData]) -> TechnicalsContextReader:
        return TechnicalsContextReader(context)
