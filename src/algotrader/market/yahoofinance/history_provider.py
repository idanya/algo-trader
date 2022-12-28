from datetime import datetime
from typing import List

import yfinance as yf

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan


class YahooFinanceHistoryProvider:
    def get_symbol_history(self, symbol: str, period: TimeSpan, interval: TimeSpan,
                           start_time: datetime, end_time: datetime, auto_adjust: bool = True,
                           include_after_hours: bool = False) -> List[Candle]:
        """
        @param symbol: symbol
        @param period: time span of each candle
        @param interval: interval between candles
        @param start_time: first candle time
        @param end_time: latest candle time
        @param auto_adjust: auto adjust closing price (dividends, splits)
        @param include_after_hours: include pre and post market data
        @return: List of candles
        """
        ticker = yf.Ticker(symbol)
        data = ticker.history(self._translate_timespan(period),
                              self._translate_timespan(interval),
                              start_time, end_time, include_after_hours,
                              False, auto_adjust)

        candles: List[Candle] = []
        for index, row in data.iterrows():
            candle = Candle(symbol, period, index.to_pydatetime(),
                            row['Open'], row['Close'], row['High'], row['Low'], row['Volume'])
            candles.append(candle)

        return candles

    @staticmethod
    def _translate_timespan(span: TimeSpan) -> str:
        if span == TimeSpan.Day:
            return '1d'
        elif span == TimeSpan.Hour:
            return '1h'
        elif span == TimeSpan.Minute:
            return '1m'
        else:
            raise ValueError('minimum timespan for yahoo finance is 1m')
