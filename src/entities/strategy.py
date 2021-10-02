from abc import abstractmethod

from entities.candle import Candle
from entities.strategy_signal import StrategySignal


class Strategy:
    @abstractmethod
    def process(self, candle: Candle) -> StrategySignal:
        pass
