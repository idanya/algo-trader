import logging
from typing import List, Dict

from algotrader.entities.candle import Candle
from algotrader.entities.strategy_signal import StrategySignal, SignalDirection
from algotrader.trade.signals_executor import SignalsExecutor

DEFAULT_ORDER_VALUE = 10000


class SimpleSumSignalsExecutor(SignalsExecutor):
    def __init__(self) -> None:
        self.position: Dict[str, float] = {}
        self.cash = 0

    def _get_order_size(self, price: float) -> float:
        return DEFAULT_ORDER_VALUE / price

    def execute(self, candle: Candle, signals: List[StrategySignal]):
        # close when there is no signal
        if len(signals) == 0 and candle.symbol in self.position and self.position[candle.symbol] != 0:
            self.cash += candle.close * self.position[candle.symbol]
            self.position[candle.symbol] = 0

        for signal in signals:
            logging.info(f"Got {signal.direction} signal for {signal.symbol}. Signaling candle: {candle.serialize()}")

            if signal.symbol not in self.position:
                self.position[signal.symbol] = 0

            # don't act if we already have a position
            if self.position[signal.symbol] != 0:
                continue

            order_size = self._get_order_size(candle.close)

            if signal.direction == SignalDirection.Long:
                self.position[signal.symbol] += order_size
                self.cash -= candle.close * order_size
            else:
                self.position[signal.symbol] -= order_size
                self.cash += candle.close * order_size

        non_zero_postitions = {k: v for k, v in self.position.items() if v > 0}
        if len(non_zero_postitions) > 0:
            logging.info(f"Position: {non_zero_postitions} | Cash: {self.cash}")
