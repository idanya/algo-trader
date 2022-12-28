from typing import List

from algotrader.entities.candle import Candle
from algotrader.entities.strategy import Strategy
from algotrader.entities.strategy_signal import StrategySignal, SignalDirection
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.processors.technicals import INDICATORS_ATTACHMENT_KEY, Indicators
from algotrader.pipeline.shared_context import SharedContext


class SimpleSMA(Strategy):
    """
    Simple Moving average strategy
    """

    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        cache_reader = CandleCache.context_reader(context)
        symbol_candles = cache_reader.get_symbol_candles(candle.symbol)

        if not symbol_candles or len(symbol_candles) < 1:
            return []

        past_candle_indicators: Indicators = symbol_candles[-1].attachments.get_attachment(INDICATORS_ATTACHMENT_KEY)
        current_candle_indicators: Indicators = candle.attachments.get_attachment(INDICATORS_ATTACHMENT_KEY)

        if not current_candle_indicators.has('sma20') or not past_candle_indicators.has('sma20'):
            return []

        if current_candle_indicators['sma5'] > current_candle_indicators['sma20'] and \
                past_candle_indicators['sma5'] < past_candle_indicators['sma20']:
            return [StrategySignal(candle.symbol, SignalDirection.Long)]

        if current_candle_indicators['sma5'] < current_candle_indicators['sma20'] and \
                past_candle_indicators['sma5'] > past_candle_indicators['sma20']:
            return [StrategySignal(candle.symbol, SignalDirection.Short)]
