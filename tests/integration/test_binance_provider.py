import os
import threading
from datetime import datetime, timedelta
from unittest import TestCase

from dotenv import load_dotenv

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.providers.binance import BinanceProvider

load_dotenv()


class TestBinanceMarketProvider(TestCase):
    SYMBOL = 'BTCUSDT'
    BASE_TIME = datetime.fromtimestamp(1671183359)
    API_KEY = os.environ.get('BINANCE_API_KEY')
    API_SECRET = os.environ.get('BINANCE_API_SECRET')

    def test_get_account(self):
        provider = BinanceProvider(self.API_KEY, self.API_SECRET, False, testnet=True)
        provider.account()

    def test_get_symbol_history(self):
        provider = BinanceProvider(self.API_KEY, self.API_SECRET, False)

        from_time = self.BASE_TIME - timedelta(days=50)
        to_time = self.BASE_TIME
        candles = provider.get_symbol_history(self.SYMBOL, TimeSpan.Day, from_time, to_time)

        self.assertEqual(len(candles), 50)
        for candle in candles:
            self.assertTrue(from_time <= candle.timestamp <= to_time)
            self._assert_candles_values(candle)

    def test_get_kline_stream(self):
        provider = BinanceProvider(self.API_KEY, self.API_SECRET, True)
        event: threading.Event = threading.Event()

        def handler(candle: Candle):
            self._assert_candles_values(candle)
            event.set()

        provider.start_kline_socket(self.SYMBOL, TimeSpan.Second, handler)
        event.wait()

    def _assert_candles_values(self, candle: Candle):
        self.assertEqual(candle.symbol, self.SYMBOL)
        self.assertTrue(candle.high > candle.low)
        self.assertTrue(candle.volume > 0)
