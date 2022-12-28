from datetime import datetime, timedelta
from typing import List
from unittest import TestCase

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.market.yahoofinance.history_provider import YahooFinanceHistoryProvider
from algotrader.pipeline.sources.yahoo_finance_history import YahooFinanceHistorySource


class TestYahooMarketSource(TestCase):
    provider = YahooFinanceHistoryProvider()
    symbols = ['AAPL', 'MSFT']
    to_time = datetime.fromtimestamp(1669145312)
    from_time = to_time - timedelta(days=50)

    def test_quick_source(self):
        source = YahooFinanceHistorySource(self.symbols, TimeSpan.Day, self.from_time, self.to_time)
        candles = list(source.read())
        self._assert_sanity_response(candles)

    def test_sorted_source(self):
        source = YahooFinanceHistorySource(self.symbols, TimeSpan.Day, self.from_time, self.to_time, sort_all=True)
        candles = list(source.read())
        self._assert_sanity_response(candles)

        for i in range(1, len(candles)):
            self.assertTrue(candles[i].timestamp >= candles[i - 1].timestamp)

    def _assert_sanity_response(self, candles: List[Candle]):
        self.assertEqual(len(candles) % 2, 0)

        for candle in candles:
            self.assertIn(candle.symbol, self.symbols)
