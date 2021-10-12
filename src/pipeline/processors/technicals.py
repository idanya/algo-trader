from __future__ import annotations

from typing import Optional, List, Dict, Union, Tuple

from calc.technicals import TechnicalCalculator
from entities.candle import Candle
from entities.serializable import Deserializable, Serializable
from pipeline.processor import Processor
from pipeline.processors.candle_cache import CandleCache
from pipeline.shared_context import SharedContext

CONTEXT_IDENT = 'Technicals'
INDICATORS_ATTACHMENT_KEY = 'indicators'
TechnicalsData = Dict[str, Dict[str, List[float]]]


class Indicators(Serializable, Deserializable):
    def __init__(self) -> None:
        super().__init__()
        self.indicators: Dict[str, Union[List[float], float]] = {}

    def __getitem__(self, key):
        return self.indicators[key]

    @classmethod
    def deserialize(cls, data: Dict) -> Indicators:
        obj = Indicators()
        obj.indicators = data
        return obj

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update(self.indicators)
        return obj

    def has(self, key: str):
        return key in self.indicators and self.indicators[key] is not None


class TechnicalsProcessor(Processor):

    def __init__(self, next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)

    def process(self, context: SharedContext, candle: Candle):
        cache_reader = CandleCache.context_reader(context)
        symbol_candles = cache_reader.get_symbol_candles(candle.symbol) or []
        calculator = TechnicalCalculator(symbol_candles + [candle])

        candle_indicators = Indicators()
        self._calculate(calculator, candle_indicators)
        candle.attachments.add_attachement(INDICATORS_ATTACHMENT_KEY, candle_indicators)

        if self.next_processor:
            self.next_processor.process(context, candle)

    @staticmethod
    def _calculate(calculator: TechnicalCalculator, candle_indicators: Indicators):
        candle_indicators.indicators['sma5'] = TechnicalsProcessor._get_last_value(calculator.sma(5))
        candle_indicators.indicators['sma20'] = TechnicalsProcessor._get_last_value(calculator.sma(20))
        candle_indicators.indicators['sma50'] = TechnicalsProcessor._get_last_value(calculator.sma(50))
        candle_indicators.indicators['cci7'] = TechnicalsProcessor._get_last_value(calculator.cci(7))
        candle_indicators.indicators['macd'] = TechnicalsProcessor._get_last_value(calculator.macd(2, 5, 9))
        candle_indicators.indicators['rsi2'] = TechnicalsProcessor._get_last_value(calculator.rsi(2))

    @staticmethod
    def _get_last_value(values: Union[Tuple[List[float]], List[float]]) -> Optional[Union[List[float], float]]:
        if isinstance(values, tuple):
            return [v[-1] for v in values]
        elif isinstance(values, list) and values:
            return values[-1]
