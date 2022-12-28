from datetime import datetime

from algotrader.entities.timespan import TimeSpan
from algotrader.market.async_market_provider import AsyncMarketProvider, AsyncQueryResult
from algotrader.providers.ib.interactive_brokers_connector import InteractiveBrokersConnector


class IBMarketProvider(AsyncMarketProvider):

    def __init__(self, ib_connector: InteractiveBrokersConnector) -> None:
        super().__init__()
        self.ib_connector = ib_connector

    def request_symbol_history(self, symbol: str, candle_timespan: TimeSpan, from_time: datetime,
                               to_time: datetime) -> AsyncQueryResult:
        return self.ib_connector.request_symbol_history(symbol, candle_timespan, from_time, to_time)
