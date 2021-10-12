from typing import Iterator

from entities.candle import Candle
from pipeline.source import Source


class ReverseSource(Source):
    def __init__(self, source: Source) -> None:
        super().__init__()
        self.source = source

    def read(self) -> Iterator[Candle]:
        candles = list(self.source.read())
        candles.reverse()

        for c in candles:
            yield c
