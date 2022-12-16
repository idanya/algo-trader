from datetime import datetime, timedelta
from unittest import TestCase

from entities.timespan import TimeSpan
from providers.binance import BinanceProvider


class TestBinanceMarketProvider(TestCase):
    BASE_TIME = datetime.fromtimestamp(1671183359)

    def test_get_symbol_history(self):
        from_time = self.BASE_TIME - timedelta(days=50)
        to_time = self.BASE_TIME
        provider = BinanceProvider()
        candles = provider.get_symbol_history('BTCUSDT', TimeSpan.Day, from_time, to_time)

        self.assertEqual(len(candles), 50)
        for candle in candles:
            self.assertTrue(from_time <= candle.timestamp <= to_time)
            self.assertEqual(candle.symbol, 'BTCUSDT')
            self.assertTrue(candle.high > candle.low)
            self.assertTrue(candle.volume > 0)
