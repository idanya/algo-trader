from typing import List, Iterator

from algotrader.entities.candle import Candle
from algotrader.pipeline.source import Source


class FakeSource(Source):
    def __init__(self, candles: List[Candle]) -> None:
        super().__init__()
        self.candles = candles
        self.candles.sort(key=lambda c: c.timestamp)

    def read(self) -> Iterator[Candle]:
        for c in self.candles:
            yield c
