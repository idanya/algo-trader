from datetime import datetime
from typing import List, Dict, Iterator

from entities.candle import Candle
from entities.timespan import TimeSpan
from storage.storage_provider import StorageProvider


class InMemoryStorage(StorageProvider):

    def __init__(self) -> None:
        super().__init__()
        self.candles: Dict[str, List[Candle]] = {}

    def get_symbol_candles(self, symbol: str, time_span: TimeSpan, from_timestamp: datetime,
                           to_timestamp: datetime) -> List[Candle]:

        if symbol not in self.candles:
            return []

        return list(filter(lambda candle:
                           candle.time_span == time_span and
                           from_timestamp <= candle.timestamp <= to_timestamp, self.candles[symbol]))

    def get_candles(self, time_span: TimeSpan, from_timestamp: datetime, to_timestamp: datetime) -> List[Candle]:

        def all_candles() -> Iterator[Candle]:
            for sym_candles in self.candles.values():
                for c in sym_candles:
                    yield c

        return list(filter(lambda candle:
                           candle.time_span == time_span and
                           from_timestamp <= candle.timestamp <= to_timestamp, all_candles()))

    def save(self, candle: Candle):
        if candle.symbol not in self.candles:
            self.candles[candle.symbol] = []

        self.candles[candle.symbol].append(candle)
        self.candles[candle.symbol].sort(key=lambda c: c.timestamp)
