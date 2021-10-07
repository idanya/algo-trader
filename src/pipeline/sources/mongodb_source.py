from datetime import datetime
from typing import Iterator, List, Optional

from entities.candle import Candle
from entities.timespan import TimeSpan
from pipeline.source import Source
from storage.mongodb_storage import MongoDBStorage


class MongoDBSource(Source):

    def __init__(self, mongo_storage: MongoDBStorage, symbols: List[str], timespan: TimeSpan,
                 from_time: datetime, to_time: Optional[datetime] = datetime.now()) -> None:
        self.timespan = timespan
        self.to_time = to_time
        self.from_time = from_time
        self.mongo_storage = mongo_storage
        self.symbols = symbols

    def read(self) -> Iterator[Candle]:
        all_candles = self.mongo_storage.get_candles(self.timespan, self.from_time, self.to_time)
        for c in all_candles:
            if c.symbol in self.symbols:
                yield c
