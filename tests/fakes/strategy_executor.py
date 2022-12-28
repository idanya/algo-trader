from typing import Callable, List

from algotrader.entities.candle import Candle
from algotrader.entities.strategy_signal import StrategySignal
from algotrader.trade.signals_executor import SignalsExecutor

ExecuterCallback = Callable[[List[StrategySignal]], None]


class FakeSignalsExecutor(SignalsExecutor):
    def __init__(self, callback: ExecuterCallback) -> None:
        super().__init__()
        self.callback = callback

    def execute(self, candle: Candle, signals: List[StrategySignal]):
        self.callback(signals)
