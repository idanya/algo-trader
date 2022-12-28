from datetime import datetime
from typing import List
from unittest import TestCase

from algotrader.entities.candle import Candle
from algotrader.entities.strategy import Strategy
from algotrader.entities.strategy_signal import StrategySignal, SignalDirection
from algotrader.entities.timespan import TimeSpan
from fakes.strategy_executor import FakeSignalsExecutor
from algotrader.pipeline.processors.strategy import StrategyProcessor
from algotrader.pipeline.shared_context import SharedContext
from unit import TEST_SYMBOL, generate_candle


class DummyStrategy(Strategy):
    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        return [StrategySignal(candle.symbol, SignalDirection.Long)]


class NoSignalStrategy(Strategy):
    def process(self, context: SharedContext, candle: Candle) -> List[StrategySignal]:
        return []


class TestStrategyProcessor(TestCase):
    def test_signal_strategy(self):
        def _check(signals: List[StrategySignal]):
            self.assertEqual(1, len(signals))
            self.assertEqual(SignalDirection.Long, signals[0].direction)
            self.assertEqual(TEST_SYMBOL, signals[0].symbol)

        candle = generate_candle(TimeSpan.Day, datetime.now())
        processor = StrategyProcessor([DummyStrategy()], FakeSignalsExecutor(_check), None)
        processor.process(SharedContext(), candle)

    def test_multiple_strategies(self):
        def _check(signals: List[StrategySignal]):
            self.assertEqual(3, len(signals))
            for i in range(3):
                self.assertEqual(SignalDirection.Long, signals[i].direction)
                self.assertEqual(TEST_SYMBOL, signals[i].symbol)

        candle = generate_candle(TimeSpan.Day, datetime.now())
        processor = StrategyProcessor([DummyStrategy()] * 3, FakeSignalsExecutor(_check), None)
        processor.process(SharedContext(), candle)

    def test_no_signal(self):
        def _check(signals: List[StrategySignal]):
            self.assertEqual(0, len(signals))

        candle = generate_candle(TimeSpan.Day, datetime.now())
        processor = StrategyProcessor([NoSignalStrategy()], FakeSignalsExecutor(_check), None)
        processor.process(SharedContext(), candle)
