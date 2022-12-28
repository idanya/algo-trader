import logging
from datetime import datetime
from typing import Iterator, List, Dict

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.market.yahoofinance.history_provider import YahooFinanceHistoryProvider
from algotrader.pipeline.source import Source


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
        logging.info(f'Fetching {symbol} history from Yahoo Finance')
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

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'symbols': self.symbols,
            'timespan': self.timespan.value,
            'start_time': self.start_time.timestamp(),
            'end_time': self.end_time.timestamp(),
            'auto_adjust': self.auto_adjust,
            'include_after_hours': self.include_after_hours,
            'sort_all': self.sort_all,
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        return cls(data.get('symbols'), TimeSpan(data.get('timespan')), datetime.fromtimestamp(data.get('start_time')),
                   datetime.fromtimestamp(data.get('end_time')), data.get('auto_adjust'),
                   data.get('include_after_hours'), data.get('sort_all'))
