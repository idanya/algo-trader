from abc import abstractmethod
from datetime import datetime

from entities.timespan import TimeSpan
from market.async_query_result import AsyncQueryResult


class AsyncMarketProvider:
    @abstractmethod
    def request_symbol_history(self, symbol: str, candle_timespan: TimeSpan, from_time: datetime,
                               to_time: datetime) -> AsyncQueryResult:
        pass
