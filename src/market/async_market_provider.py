import threading
from abc import abstractmethod
from datetime import datetime
from typing import Callable, List

from entities.candle import Candle
from entities.timespan import TimeSpan
from providers.ib.query_subscription import QuerySubscription

CandlesCallback = Callable[[List[Candle]], None]


class AsyncQueryResult:
    def __init__(self, from_timestamp: datetime, to_timestamp: datetime) -> None:
        self.from_timestamp = from_timestamp
        self.to_timestamp = to_timestamp
        self.done_event = threading.Event()
        self.subscriptions: List[QuerySubscription] = []
        self.candles: List[Candle] = []

    def attach_query_subscription(self, subscription: QuerySubscription):
        self.subscriptions.append(subscription)

    def result(self) -> List[Candle]:
        results = [sub.result() for sub in self.subscriptions]
        candles: List[Candle] = []
        for res in results:
            candles += res

        filtered_candles = filter(lambda c: self.from_timestamp < c.timestamp < self.to_timestamp, candles)
        return sorted(filtered_candles, key=lambda c: c.timestamp)


class AsyncMarketProvider:
    @abstractmethod
    def request_symbol_history(self, symbol: str, candle_timespan: TimeSpan, from_time: datetime,
                               to_time: datetime) -> AsyncQueryResult:
        pass
