from typing import Callable, List

from entities.strategy_signal import StrategySignal
from trade.signals_executor import SignalsExecutor

ExecuterCallback = Callable[[List[StrategySignal]], None]


class FakeStrategyExecutor(SignalsExecutor):
    def __init__(self, callback: ExecuterCallback) -> None:
        super().__init__()
        self.callback = callback

    def execute(self, signals: List[StrategySignal]):
        self.callback(signals)
