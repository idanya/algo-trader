from abc import abstractmethod
from typing import Iterator

from entities.candle import Candle


class Source:
    @abstractmethod
    def read(self) -> Iterator[Candle]:
        pass


