import logging
from datetime import datetime
from typing import Iterator, List, Optional, Dict

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.source import Source
from algotrader.storage.mongodb_storage import MongoDBStorage


class MongoDBSource(Source):
    """
    Source for fetching data from MongoDB
    """
    logger = logging.getLogger('MongoDBSource')

    def __init__(self, mongo_storage: MongoDBStorage, symbols: List[str], timespan: TimeSpan,
                 from_time: datetime, to_time: Optional[datetime] = datetime.now()) -> None:
        """
        @param mongo_storage: MongoDBStorage instance
        @param symbols: list of symbols to fetch
        @param timespan: timespan of candles
        @param from_time: time to start fetching from
        @param to_time: time to fetch to
        """
        self.timespan = timespan
        self.to_time = to_time
        self.from_time = from_time
        self.mongo_storage = mongo_storage
        self.symbols = symbols

    def read(self) -> Iterator[Candle]:
        self.logger.info('Fetching candles from mongo source...')
        all_candles = self.mongo_storage.get_candles(self.timespan, self.from_time, self.to_time)
        self.logger.info('Got candles, starting iteration')
        for c in all_candles:
            if c.symbol in self.symbols:
                yield c

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'mongo_storage': self.mongo_storage.serialize(),
            'symbols': self.symbols,
            'timespan': self.timespan.value,
            'from_time': self.from_time,
            'to_time': self.to_time,
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        storage = MongoDBStorage.deserialize(data.get('mongo_storage'))
        return cls(storage, data.get('symbols'), TimeSpan(data.get('timespan')), data.get('from_time'), data.get('to_time'))
