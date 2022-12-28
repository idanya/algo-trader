from datetime import datetime, timedelta
from unittest import TestCase

from algotrader.entities.timespan import TimeSpan
from algotrader.market.yahoofinance.history_provider import YahooFinanceHistoryProvider


class TestYahooMarketProvider(TestCase):
    def test_get_symbol_history(self):
        from_time = datetime.now() - timedelta(days=50)
        to_time = datetime.now()
        provider = YahooFinanceHistoryProvider()
        result = provider.get_symbol_history('AAPL', TimeSpan.Day, TimeSpan.Day, from_time, to_time)
        self.assertTrue(len(result) > 10)
        self.assertIsNotNone(result)
        for candle in result:
            self.assertEqual('AAPL', candle.symbol)
            self.assertTrue(0 < candle.open)
            self.assertTrue(0 < candle.close)
            self.assertTrue(0 < candle.volume)
            self.assertTrue(to_time.date() >= candle.timestamp.date() >= from_time.date())
            self.assertTrue(0 < candle.low < candle.high)
