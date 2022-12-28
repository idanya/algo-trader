from typing import List, Optional, Dict

from algotrader.entities.candle import Candle
from algotrader.entities.strategy import Strategy
from algotrader.entities.strategy_signal import StrategySignal, SignalDirection
from algotrader.pipeline.processors.candle_cache import CandleCache
from algotrader.pipeline.processors.technicals import INDICATORS_ATTACHMENT_KEY, Indicators
from algotrader.pipeline.shared_context import SharedContext


class ConnorsRSI2(Strategy):

    def __init__(self) -> None:
        super().__init__()
        self.current_position: Dict[str, Optional[SignalDirection]] = {}

    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        cache_reader = CandleCache.context_reader(context)
        symbol_candles = cache_reader.get_symbol_candles(candle.symbol)

        if not symbol_candles or len(symbol_candles) < 1:
            return []

        if candle.symbol not in self.current_position:
            self.current_position[candle.symbol] = None

        past_candle_indicators: Indicators = symbol_candles[-1].attachments.get_attachment(
            INDICATORS_ATTACHMENT_KEY)
        current_candle_indicators: Indicators = candle.attachments.get_attachment(
            INDICATORS_ATTACHMENT_KEY)

        if not current_candle_indicators.has('rsi2') \
                or not current_candle_indicators.has('sma50') \
                or not past_candle_indicators.has('rsi2'):
            return []

        if self.current_position[candle.symbol] == SignalDirection.Long:
            if candle.close > current_candle_indicators['sma5']:
                self.current_position[candle.symbol] = None
                return [StrategySignal(candle.symbol, SignalDirection.Short)]

            return []

        if self.current_position[candle.symbol] == SignalDirection.Short:
            if candle.close < current_candle_indicators['sma5']:
                self.current_position[candle.symbol] = None
                return [StrategySignal(candle.symbol, SignalDirection.Long)]

            return []

        if candle.close > current_candle_indicators['sma50'] and \
                current_candle_indicators['rsi2'] < 10 < past_candle_indicators['rsi2']:
            self.current_position[candle.symbol] = SignalDirection.Long
            return [StrategySignal(candle.symbol, SignalDirection.Long)]

        if candle.close < current_candle_indicators['sma50'] and \
                current_candle_indicators['rsi2'] > 90 > past_candle_indicators['rsi2']:
            self.current_position[candle.symbol] = SignalDirection.Short
            return [StrategySignal(candle.symbol, SignalDirection.Short)]
