from abc import abstractmethod
from typing import List

from entities.candle import Candle
from entities.strategy_signal import StrategySignal


class SignalsExecutor:
    @abstractmethod
    def execute(self, candle: Candle, signals: List[StrategySignal]):
        pass
