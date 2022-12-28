from abc import abstractmethod
from typing import Iterator

from entities.candle import Candle
from entities.serializable import Deserializable, Serializable


class Source(Serializable, Deserializable):
    @abstractmethod
    def read(self) -> Iterator[Candle]:
        pass
