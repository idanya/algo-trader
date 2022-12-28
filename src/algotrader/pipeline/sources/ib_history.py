import logging
from datetime import datetime
from typing import Iterator, List, Optional

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.market.ib_market import IBMarketProvider
from algotrader.pipeline.source import Source
from algotrader.providers.ib.interactive_brokers_connector import InteractiveBrokersConnector


class IBHistorySource(Source):
    """
    Source for fetching data from Interactive Brokers
    """
    def __init__(self, ib_connector: InteractiveBrokersConnector, symbols: List[str], timespan: TimeSpan,
                 from_time: datetime, to_time: Optional[datetime] = datetime.now()) -> None:
        """
        @param ib_connector: InteractiveBrokersConnector instance
        @param symbols: symbols to fetch
        @param timespan: timespan of candles
        @param from_time: time to start fetching from
        @param to_time: time to fetch to
        """
        self.timespan = timespan
        self.to_time = to_time
        self.from_time = from_time
        self.marketProvider = IBMarketProvider(ib_connector)
        self.symbols = symbols

    def read(self) -> Iterator[Candle]:
        for symbol in self.symbols:
            try:
                result = self.marketProvider.request_symbol_history(symbol, self.timespan, self.from_time, self.to_time)
                for candle in result.result():
                    yield candle
            except Exception as ex:
                logging.warning(f'Failed to fetch symbol {symbol} history. Error: {ex}')
