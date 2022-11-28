from datetime import datetime
from typing import Iterator, List

from entities.candle import Candle
from entities.timespan import TimeSpan
from market.yahoofinance.history_provider import YahooFinanceHistoryProvider
from pipeline.source import Source


class YahooFinanceHistorySource(Source):
    """
    Source for fetching historical data from Yahoo Finance
    """

    def __init__(self, symbols: List[str], timespan: TimeSpan,
                 start_time: datetime, end_time: datetime, auto_adjust: bool = True,
                 include_after_hours: bool = False, sort_all: bool = False):
        """
        @param symbols: list of symbols to fetch
        @param timespan: candles timespan
        @param start_time: first candle time
        @param end_time: latest candle time
        @param auto_adjust: auto adjust closing price (dividends, splits)
        @param include_after_hours: include pre and post market data
        @param sort_all: sort candles by time cross symbols (will start streaming candles only after all
        symbols fetched (slower for first response)
        """
        self.sort_all = sort_all
        self.symbols = symbols
        self.auto_adjust = auto_adjust
        self.include_after_hours = include_after_hours
        self.end_time = end_time
        self.start_time = start_time
        self.timespan = timespan
        self.provider = YahooFinanceHistoryProvider()

    def fetch_symbol(self, symbol: str) -> Iterator[Candle]:
        candles = self.provider.get_symbol_history(symbol, self.timespan, self.timespan, self.start_time, self.end_time,
                                                   self.auto_adjust, self.include_after_hours)
        for candle in candles:
            yield candle

    def _read_quick(self) -> Iterator[Candle]:
        for symbol in self.symbols:
            for candle in self.fetch_symbol(symbol):
                yield candle

    def _read_sort(self) -> List[Candle]:
        candles: List[Candle] = []
        for symbol in self.symbols:
            candles.extend(self.fetch_symbol(symbol))

        return sorted(candles, key=lambda candle: candle.timestamp)

    def read(self) -> Iterator[Candle]:
        if self.sort_all:
            for candle in self._read_sort():
                yield candle
        else:
            for candle in self._read_quick():
                yield candle
