from datetime import datetime
from unittest import TestCase

from algotrader.entities.strategy_signal import StrategySignal, SignalDirection
from algotrader.entities.timespan import TimeSpan
from algotrader.trade.simple_sum_signals_executor import DEFAULT_ORDER_VALUE, SimpleSumSignalsExecutor
from unit import TEST_SYMBOL, generate_candle_with_price


class TestSimpleSumSignalsExecutor(TestCase):
    def test_open_and_close_long(self):
        executor = SimpleSumSignalsExecutor()
        candle = generate_candle_with_price(TimeSpan.Day, datetime.now(), DEFAULT_ORDER_VALUE)
        signal = StrategySignal(TEST_SYMBOL, SignalDirection.Long)
        # test opening a long trade
        executor.execute(candle, [signal])
        self.assertEqual(1, executor.position[TEST_SYMBOL])
        self.assertEqual(-DEFAULT_ORDER_VALUE, executor.cash)
        # test closing a long trade
        candle = generate_candle_with_price(TimeSpan.Day, datetime.now(), DEFAULT_ORDER_VALUE + 88)
        executor.execute(candle, [])
        self.assertEqual(0, executor.position[TEST_SYMBOL])
        self.assertEqual(88, executor.cash)

    def test_open_and_close_short(self):
        executor = SimpleSumSignalsExecutor()
        candle = generate_candle_with_price(TimeSpan.Day, datetime.now(), DEFAULT_ORDER_VALUE)
        signal = StrategySignal(TEST_SYMBOL, SignalDirection.Short)
        # test opening a short trade
        executor.execute(candle, [signal])
        self.assertEqual(-1, executor.position[TEST_SYMBOL])
        self.assertEqual(DEFAULT_ORDER_VALUE, executor.cash)
        # test closing a short trade
        candle = generate_candle_with_price(TimeSpan.Day, datetime.now(), DEFAULT_ORDER_VALUE - 88)
        executor.execute(candle, [])
        self.assertEqual(0, executor.position[TEST_SYMBOL])
        self.assertEqual(88, executor.cash)
