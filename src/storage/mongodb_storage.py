from datetime import datetime
from typing import List, Dict

import pymongo

from entities.candle import Candle, str_to_timestamp, timestamp_to_str
from entities.timespan import TimeSpan
from storage.storage_provider import StorageProvider

DB_NAME = 'algo-trader'
CANDLES_COLLECTION = 'candles'


class MongoDBStorage(StorageProvider):

    def __init__(self, host: str = 'localhost', port: int = 27017, database: str = DB_NAME) -> None:
        super().__init__()
        self.client = pymongo.MongoClient(f'mongodb://{host}:{port}/')
        self.db = self.client[database]
        self.candles_collection = self.db[CANDLES_COLLECTION]
        self.candles_collection.create_index([("symbol", pymongo.ASCENDING),
                                              ("timespan", pymongo.ASCENDING),
                                              ("timestamp", pymongo.ASCENDING)],
                                             unique=True, background=True)

    def save(self, candle: Candle):
        self.candles_collection.replace_one(self._serialize_candle_key(candle), self._serialize_candle(candle),
                                            upsert=True)
        # self.candles_collection.insert_one(self._serialize_candle(candle))

    def _serialize_candle_key(self, candle: Candle) -> Dict:
        data = self._serialize_candle(candle)
        return {
            'symbol': data['symbol'],
            'timespan': data['timespan'],
            'timestamp': data['timestamp'],
        }

    def _serialize_candle(self, candle: Candle) -> Dict:
        data = candle.serialize()
        data['timestamp'] = str_to_timestamp(data['timestamp'])
        return data

    def _deserialize_candle(self, data: Dict) -> Candle:
        data['timestamp'] = timestamp_to_str(data['timestamp'])
        return Candle.deserialize(data)

    def get_candles(self, symbol: str, time_span: TimeSpan,
                    from_timestamp: datetime, to_timestamp: datetime) -> List[
        Candle]:
        query = {
            'symbol': symbol,
            'timespan': time_span.name,
            'timestamp': {"$gte": from_timestamp, "$lte": to_timestamp}
        }

        return [self._deserialize_candle(candle) for candle in self.candles_collection.find(query).sort("timestamp")]

    def __drop_collections__(self):
        self.db.drop_collection(CANDLES_COLLECTION)
