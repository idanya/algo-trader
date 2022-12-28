from datetime import datetime, timedelta
from unittest import TestCase

from algotrader.entities.timespan import TimeSpan
from algotrader.market.async_market_provider import AsyncQueryResult
from algotrader.market.ib_market import IBMarketProvider
from algotrader.providers.ib.interactive_brokers_connector import InteractiveBrokersConnector


class TestIBMarketProvider(TestCase):

    def setUp(self) -> None:
        super().setUp()
        self.ib_connector = InteractiveBrokersConnector()

    def tearDown(self) -> None:
        super().tearDown()
        self.ib_connector.kill()

    def test_daily_history(self):
        ib_provider = IBMarketProvider(self.ib_connector)
        from_time = datetime.now() - timedelta(days=50)
        to_time = datetime.now() - timedelta(days=30)

        async_result: AsyncQueryResult = ib_provider.request_symbol_history('AAPL', TimeSpan.Day, from_time, to_time)
        candles = async_result.result()
        self.assertTrue(len(candles) > 10)
        self.assertTrue(candles[0].timestamp < candles[-1].timestamp)

    def test_current_day_history(self):
        ib_provider = IBMarketProvider(self.ib_connector)

        yesterday = (datetime.now() - timedelta(days=1)).date()
        yesterday = datetime(yesterday.year, yesterday.month, yesterday.day)
        async_result: AsyncQueryResult = ib_provider.request_symbol_history('AAPL', TimeSpan.Day, yesterday,
                                                                            datetime.now())
        candles = async_result.result()
        self.assertEqual(1, len(candles))
        self.assertEqual(yesterday.date(), candles[0].timestamp.date())

    def test_yearly_history(self):
        ib_provider = IBMarketProvider(self.ib_connector)
        from_time = datetime.now() - timedelta(days=500)
        to_time = datetime.now() - timedelta(days=100)

        async_result: AsyncQueryResult = ib_provider.request_symbol_history('AAPL', TimeSpan.Day, from_time, to_time)
        candles = async_result.result()
        self.assertTrue(len(candles) > 10)
        self.assertTrue(candles[0].timestamp < candles[-1].timestamp)
        self.assertTrue(candles[0].timestamp.year < candles[-1].timestamp.year)

        self.assertEqual(candles[0].timestamp.year, from_time.year)
        self.assertEqual(candles[0].timestamp.month, from_time.month)

        self.assertEqual(candles[-1].timestamp.year, to_time.year)
        self.assertEqual(candles[-1].timestamp.month, to_time.month)
