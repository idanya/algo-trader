import logging
from typing import List

from entities.candle import Candle
from entities.strategy_signal import StrategySignal, SignalDirection
from trade.signals_executor import SignalsExecutor


class SimpleSumSignalsExecutor(SignalsExecutor):

    def __init__(self) -> None:
        self.sum = 0

    def execute(self, candle: Candle, signals: List[StrategySignal]):
        for signal in signals:
            logging.info(f"Got {signal.direction} signal for {signal.symbol}. Signaling candle: {candle.serialize()}")
            if signal.direction == SignalDirection.Long:
                self.sum -= candle.close
            else:
                self.sum += candle.close

        logging.info(f"New sum = {self.sum}")
