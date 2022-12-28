from abc import abstractmethod
from typing import Iterator

from algotrader.entities.candle import Candle
from algotrader.entities.serializable import Deserializable, Serializable


class Source(Serializable, Deserializable):
    @abstractmethod
    def read(self) -> Iterator[Candle]:
        pass
