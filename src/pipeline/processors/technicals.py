from __future__ import annotations

from typing import Optional, List, Dict, Union, Tuple

from calc.technicals import TechnicalCalculator
from entities.candle import Candle
from entities.generic_candle_attachment import GenericCandleAttachment
from pipeline.processor import Processor
from pipeline.processors.candle_cache import CandleCache
from pipeline.shared_context import SharedContext

CONTEXT_IDENT = 'Technicals'
INDICATORS_ATTACHMENT_KEY = 'indicators'
TechnicalsData = Dict[str, Dict[str, List[float]]]

IndicatorValue = Union[List[float], float]


class Indicators(GenericCandleAttachment[IndicatorValue]):
    pass


Indicators()


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
        candle_indicators.set('sma5', TechnicalsProcessor._get_last_value(calculator.sma(5)))
        candle_indicators.set('sma20', TechnicalsProcessor._get_last_value(calculator.sma(20)))
        candle_indicators.set('sma50', TechnicalsProcessor._get_last_value(calculator.sma(50)))
        candle_indicators.set('cci7', TechnicalsProcessor._get_last_value(calculator.cci(7)))
        candle_indicators.set('macd', TechnicalsProcessor._get_last_value(calculator.macd(2, 5, 9)))
        candle_indicators.set('rsi2', TechnicalsProcessor._get_last_value(calculator.rsi(2)))

    @staticmethod
    def _get_last_value(values: Union[Tuple[List[float]], List[float]]) -> Optional[IndicatorValue]:
        if isinstance(values, tuple):
            return [v[-1] for v in values]
        elif isinstance(values, list) and values:
            return values[-1]
