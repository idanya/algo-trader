from abc import abstractmethod
from typing import List

from entities.candle import Candle
from entities.serializable import Deserializable, Serializable
from entities.strategy_signal import StrategySignal


class SignalsExecutor(Serializable, Deserializable):
    @abstractmethod
    def execute(self, candle: Candle, signals: List[StrategySignal]):
        pass
