from abc import abstractmethod
from typing import List

from algotrader.entities.candle import Candle
from algotrader.entities.serializable import Deserializable, Serializable
from algotrader.entities.strategy_signal import StrategySignal


class SignalsExecutor(Serializable, Deserializable):
    @abstractmethod
    def execute(self, candle: Candle, signals: List[StrategySignal]):
        pass
