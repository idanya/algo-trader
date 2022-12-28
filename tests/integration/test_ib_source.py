from datetime import datetime, timedelta
from unittest import TestCase

from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.sources.ib_history import IBHistorySource
from algotrader.providers.ib.interactive_brokers_connector import InteractiveBrokersConnector


class TestIBSource(TestCase):
    def setUp(self) -> None:
        super().setUp()
        self.ib_connector = InteractiveBrokersConnector()

    def tearDown(self) -> None:
        super().tearDown()
        self.ib_connector.kill()

    def test(self):
        symbol = 'AAPL'
        from_time = datetime.now() - timedelta(days=30)
        source = IBHistorySource(self.ib_connector, [symbol], TimeSpan.Day, from_time)

        candles = list(source.read())
        self.assertTrue(len(candles) > 10)

        for candle in candles:
            self.assertEqual(symbol, candle.symbol)
            self.assertEqual(TimeSpan.Day, candle.time_span)
            self.assertTrue(candle.timestamp < datetime.now())
