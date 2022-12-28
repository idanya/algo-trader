import threading
from typing import List

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan


class QuerySubscription:
    def __init__(self, query_id: int, symbol: str, candle_timespan: TimeSpan) -> None:
        self.candle_timespan = candle_timespan
        self.symbol = symbol
        self.query_id = query_id
        self.done_event = threading.Event()
        self.candles: List[Candle] = []
        self.is_error = False

    def push_candles(self, candles: List[Candle]):
        self.candles += candles

    def done(self, is_error: bool = False):
        self.is_error = is_error
        self.done_event.set()

    def result(self) -> List[Candle]:
        self.done_event.wait()

        if self.is_error:
            raise Exception('query failed. see logs.')

        return self.candles
