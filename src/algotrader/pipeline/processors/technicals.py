from __future__ import annotations

from typing import Optional, List, Dict, Union, Tuple

from algotrader.calc.technicals import TechnicalCalculator
from algotrader.entities.candle import Candle
from algotrader.entities.generic_candle_attachment import GenericCandleAttachment
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.shared_context import SharedContext

INDICATORS_ATTACHMENT_KEY = 'indicators'
TechnicalsData = Dict[str, Dict[str, List[float]]]

IndicatorValue = Union[List[float], float]


class Indicators(GenericCandleAttachment[IndicatorValue]):
    pass


Indicators()


class TechnicalsProcessor(Processor):
    """
    Technical indicators processor. Using Tulip indicators to calculate and attach technicals to the processed candles.
    Make use of the SharedContext to keep track of earlier candles.
    """

    def __init__(self, next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)

    def process(self, context: SharedContext, candle: Candle):
        cache_reader = CandleCache.context_reader(context)
        symbol_candles = cache_reader.get_symbol_candles(candle.symbol) or []
        calculator = TechnicalCalculator(symbol_candles + [candle])

        candle_indicators = Indicators()
        self._calculate(calculator, candle_indicators)
        candle.attachments.add_attachement(INDICATORS_ATTACHMENT_KEY, candle_indicators)

        super().process(context, candle)

    @staticmethod
    def _calculate(calculator: TechnicalCalculator, candle_indicators: Indicators):
        candle_indicators.set('typical', TechnicalsProcessor._get_last_value(calculator.typical()))
        candle_indicators.set('sma5', TechnicalsProcessor._get_last_value(calculator.sma(5)))
        candle_indicators.set('sma20', TechnicalsProcessor._get_last_value(calculator.sma(20)))
        candle_indicators.set('sma50', TechnicalsProcessor._get_last_value(calculator.sma(50)))
        candle_indicators.set('cci7', TechnicalsProcessor._get_last_value(calculator.cci(7)))
        candle_indicators.set('cci14', TechnicalsProcessor._get_last_value(calculator.cci(14)))
        candle_indicators.set('macd', TechnicalsProcessor._get_last_value(calculator.macd(2, 5, 9)))
        candle_indicators.set('rsi2', TechnicalsProcessor._get_last_value(calculator.rsi(2)))
        candle_indicators.set('rsi7', TechnicalsProcessor._get_last_value(calculator.rsi(7)))
        candle_indicators.set('rsi14', TechnicalsProcessor._get_last_value(calculator.rsi(14)))
        candle_indicators.set('adxr5', TechnicalsProcessor._get_last_value(calculator.adxr(5)))
        candle_indicators.set('stddev5', TechnicalsProcessor._get_last_value(calculator.stddev(5)))
        candle_indicators.set('ema5', TechnicalsProcessor._get_last_value(calculator.ema(5)))
        candle_indicators.set('ema20', TechnicalsProcessor._get_last_value(calculator.ema(20)))
        candle_indicators.set('ema50', TechnicalsProcessor._get_last_value(calculator.ema(50)))
        candle_indicators.set('mom5', TechnicalsProcessor._get_last_value(calculator.mom(5)))
        candle_indicators.set('natr5', TechnicalsProcessor._get_last_value(calculator.natr(5)))
        candle_indicators.set('meandev5', TechnicalsProcessor._get_last_value(calculator.meandev(5)))
        candle_indicators.set('obv', TechnicalsProcessor._get_last_value(calculator.obv()))
        candle_indicators.set('var5', TechnicalsProcessor._get_last_value(calculator.var(5)))
        candle_indicators.set('vosc', TechnicalsProcessor._get_last_value(calculator.vosc(2, 5)))

    @staticmethod
    def _get_last_value(values: Union[Tuple[List[float]], List[float]]) -> Optional[IndicatorValue]:
        if isinstance(values, tuple):
            return [v[-1] for v in values]
        elif isinstance(values, list) and values:
            return values[-1]
