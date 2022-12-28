from typing import Iterator, Dict

from algotrader.entities.candle import Candle
from algotrader.pipeline.source import Source


class ReverseSource(Source):
    def __init__(self, source: Source) -> None:
        super().__init__()
        self.source = source

    def read(self) -> Iterator[Candle]:
        candles = list(self.source.read())
        candles.reverse()

        for c in candles:
            yield c

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'source': self.source.serialize()
        })

        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        source: Source = Source.deserialize(data['source'])
        return cls(source)
