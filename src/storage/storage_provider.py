from abc import abstractmethod
from datetime import datetime
from typing import List

from entities.candle import Candle
from entities.timespan import TimeSpan


class StorageProvider:
    @abstractmethod
    def save(self, candle: Candle):
        pass

    @abstractmethod
    def get_candles(self, symbol: str, time_span: TimeSpan, from_timestamp: datetime,
                    to_timestamp: datetime) -> List[Candle]:
        pass
