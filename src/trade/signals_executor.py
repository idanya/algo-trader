from abc import abstractmethod
from typing import List

from entities.strategy_signal import StrategySignal


class SignalsExecutor:
    @abstractmethod
    def execute(self, signals: List[StrategySignal]):
        pass
