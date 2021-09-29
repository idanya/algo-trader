from datetime import datetime
from typing import List

import pymongo

from entities.candle import Candle
from entities.timespan import TimeSpan
from serialization.store import DeserializationService
from storage.storage_provider import StorageProvider

DB_NAME = 'algo-trader'
CANDLES_COLLECTION = 'candles'


class MongoDBStorage(StorageProvider):

    def __init__(self, host: str = 'localhost', port: int = 27017, database: str = DB_NAME) -> None:
        super().__init__()
        self.client = pymongo.MongoClient(f'mongodb://{host}:{port}/')
        self.db = self.client[database]

    def save(self, candle: Candle):
        collection = self.db[CANDLES_COLLECTION]
        collection.insert_one(candle.serialize())

    def get_candles(self, symbol: str, time_span: TimeSpan,
                    from_timestamp: datetime, to_timestamp: datetime) -> List[
        Candle]:
        collection = self.db[CANDLES_COLLECTION]

        query = {
            'symbol': symbol,
            'timespan': time_span.name,
            'timestamp': {"$gte": from_timestamp, "$lte": to_timestamp}
        }

        return [Candle.deserialize(candle) for candle in collection.find(query).sort("timestamp")]
