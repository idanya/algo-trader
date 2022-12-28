from abc import abstractmethod
from datetime import datetime

from algotrader.entities.timespan import TimeSpan
from algotrader.market.async_query_result import AsyncQueryResult


class AsyncMarketProvider:
    @abstractmethod
    def request_symbol_history(self, symbol: str, candle_timespan: TimeSpan, from_time: datetime,
                               to_time: datetime) -> AsyncQueryResult:
        pass
