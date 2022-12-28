from abc import abstractmethod
from datetime import datetime
from typing import List, Dict

from entities.candle import Candle
from entities.serializable import Deserializable, Serializable
from entities.timespan import TimeSpan


class StorageProvider(Serializable, Deserializable):
    @abstractmethod
    def save(self, candle: Candle):
        pass

    @abstractmethod
    def get_symbol_candles(self, symbol: str, time_span: TimeSpan, from_timestamp: datetime,
                           to_timestamp: datetime) -> List[Candle]:
        pass

    @abstractmethod
    def get_candles(self, time_span: TimeSpan, from_timestamp: datetime, to_timestamp: datetime) -> List[Candle]:
        pass

    @abstractmethod
    def get_aggregated_history(self, from_timestamp: datetime, to_timestamp: datetime, groupby_fields: List[str],
                               return_field: str, min_count: int, min_avg: float) -> List[Dict[str, int]]:
        pass
