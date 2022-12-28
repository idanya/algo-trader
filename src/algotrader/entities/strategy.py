from __future__ import annotations

from abc import abstractmethod
from typing import List

from entities.candle import Candle
from entities.serializable import Deserializable, Serializable
from entities.strategy_signal import StrategySignal
from pipeline.shared_context import SharedContext


class Strategy(Serializable, Deserializable):
    def __init__(self):
        pass

    @abstractmethod
    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        pass
