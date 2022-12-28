from __future__ import annotations

from abc import abstractmethod
from typing import List

from algotrader.entities.candle import Candle
from algotrader.entities.serializable import Deserializable, Serializable
from algotrader.entities.strategy_signal import StrategySignal
from algotrader.pipeline.shared_context import SharedContext


class Strategy(Serializable, Deserializable):
    def __init__(self):
        pass

    @abstractmethod
    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        pass
