import logging
from typing import List

from algotrader.entities.candle import Candle
from algotrader.entities.strategy_signal import StrategySignal
from algotrader.trade.signals_executor import SignalsExecutor


class StdoutSignalsExecutor(SignalsExecutor):
    def execute(self, candle: Candle, signals: List[StrategySignal]):
        for signal in signals:
            logging.info(f"Got {signal.direction} signal for {signal.symbol}. Signaling candle: {candle.serialize()}")
