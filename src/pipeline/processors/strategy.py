from typing import Optional, List, Dict

from entities.candle import Candle
from entities.strategy import Strategy
from entities.strategy_signal import StrategySignal
from pipeline.processor import Processor
from pipeline.shared_context import SharedContext
from serialization.store import DeserializationService
from trade.signals_executor import SignalsExecutor


class StrategyProcessor(Processor):
    def __init__(self, strategies: List[Strategy], signals_executor: SignalsExecutor,
                 next_processor: Optional[Processor]) -> None:
        super().__init__(next_processor)
        self.signals_executor = signals_executor
        self.strategies = strategies

    def process(self, context: SharedContext, candle: Candle):
        signals: List[StrategySignal] = []
        for strategy in self.strategies:
            signals += strategy.process(context, candle) or []

        self.signals_executor.execute(candle, signals)

        super().process(context, candle)

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'strategies': [strategy.serialize() for strategy in self.strategies],
            'signals_executor': self.signals_executor.serialize()
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict) -> Optional[Processor]:
        strategies: List[Strategy] = [DeserializationService.deserialize(strategy) for strategy in
                                      data.get('strategies')]
        signals_executor: SignalsExecutor = DeserializationService.deserialize(data.get('signals_executor'))
        return cls(strategies, signals_executor, cls._deserialize_next_processor(data))
