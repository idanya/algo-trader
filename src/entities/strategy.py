from abc import abstractmethod
from typing import List

from entities.candle import Candle
from entities.strategy_signal import StrategySignal
from pipeline.shared_context import SharedContext


class Strategy:
    @abstractmethod
    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        pass
