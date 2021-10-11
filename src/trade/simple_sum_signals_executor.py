import logging
from typing import List, Dict

from entities.candle import Candle
from entities.strategy_signal import StrategySignal, SignalDirection
from trade.signals_executor import SignalsExecutor


class SimpleSumSignalsExecutor(SignalsExecutor):

    def __init__(self) -> None:
        self.position: Dict[str, float] = {}
        self.cash = 0

    def execute(self, candle: Candle, signals: List[StrategySignal]):
        for signal in signals:
            logging.info(f"Got {signal.direction} signal for {signal.symbol}. Signaling candle: {candle.serialize()}")

            if signal.symbol not in self.position:
                self.position[signal.symbol] = 0

            if signal.direction == SignalDirection.Long:
                self.position[signal.symbol] += 1
                self.cash -= candle.close
            else:
                self.position[signal.symbol] -= 1
                self.cash += candle.close

        logging.info(f"Position:\n {self.position}")
        logging.info(f"Cash: {self.cash}")
