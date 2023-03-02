import json
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database

from algotrader.entities.candle import Candle, str_to_timestamp, timestamp_to_str
from algotrader.entities.timespan import TimeSpan
from algotrader.storage.storage_provider import StorageProvider

DB_NAME = 'algo-trader'
CANDLES_COLLECTION = 'candles'


class MongoDBStorage(StorageProvider):

    def __init__(self, host: str = 'localhost', port: int = 27017, database: str = DB_NAME,
                 username: str = 'root', password: str = 'root') -> None:
        self.host = host
        self.port = port
        self.database = database
        self.username = username
        self.password = password

        self.client: Optional[MongoClient] = None
        self.db: Optional[Database] = None
        self.candles_collection: Optional[Collection] = None

    def get_collection(self) -> Collection:
        self._ensure_connection()
        return self.candles_collection

    def _ensure_connection(self):
        if self.client:
            return

        self.client = pymongo.MongoClient(f'mongodb://{self.host}:{self.port}/',
                                          username=self.username, password=self.password)

        self.db = self.client[self.database]

        self.candles_collection = self.db[CANDLES_COLLECTION]
        self.candles_collection.create_index([("symbol", pymongo.ASCENDING),
                                              ("timespan", pymongo.ASCENDING),
                                              ("timestamp", pymongo.ASCENDING)],
                                             unique=True, background=True)

    def get_aggregated_history(self, from_timestamp: datetime, to_timestamp: datetime, groupby_fields: List[str],
                               return_fields: List[str], min_count: int, min_return: float) -> \
            Tuple[List[Dict[str, int]], List[Dict[str, int]]]:

        self._ensure_connection()

        stage_and_match = [
            self._generate_history_match_clause(from_timestamp, to_timestamp, groupby_fields + return_fields),
            self._generate_group_stage(groupby_fields, return_fields),
        ]

        long_pipeline = stage_and_match + [
            self._generate_min_fields_match_stage_long(min_count, return_fields, min_return)]

        short_pipeline = stage_and_match + [
            self._generate_min_fields_match_stage_short(min_count, return_fields, min_return)]

        long_matches = self._run_and_parse_aggregate(long_pipeline)
        short_matches = self._run_and_parse_aggregate(short_pipeline)

        return long_matches, short_matches

    def _run_and_parse_aggregate(self, pipeline: List):
        self._ensure_connection()

        logging.info(f'Running pipeline: {json.dumps(pipeline, indent=4, sort_keys=True, default=str)}')

        results = self.candles_collection.aggregate(pipeline, allowDiskUse=True)
        matches: List[Dict[str, int]] = []

        for res in results:
            matches.append(
                {MongoDBStorage._deserialize_group_field_name(field): value for field, value in res['_id'].items()})

        return matches

    @staticmethod
    def _generate_history_match_clause(from_timestamp: datetime, to_timestamp: datetime, fields: List[str]) -> object:
        existing_fields_query = {field: {'$exists': True} for field in fields}
        existing_fields_query.update({'timestamp': {"$gte": from_timestamp, "$lte": to_timestamp}})
        return {'$match': existing_fields_query}

    @staticmethod
    def _generate_group_stage(groupby_fields: List[str], return_fields: List[str]) -> object:
        avgs = {}
        for return_field in return_fields:
            avgs.update({MongoDBStorage._serialize_group_field_name(return_field): {'$avg': f'${return_field}'}})

        return {
            "$group": {
                "_id": {MongoDBStorage._serialize_group_field_name(field): f'${field}' for field in groupby_fields},
                **avgs,
                "count": {"$sum": 1},
            }
        }

    @staticmethod
    def _serialize_group_field_name(field: str) -> str:
        return field.replace('.', '*')

    @staticmethod
    def _deserialize_group_field_name(field: str) -> str:
        return field.replace('*', '.')

    @staticmethod
    def _generate_min_fields_match_stage_long(min_count: int, return_fields: List[str], min_return: float) -> object:
        min_returns = {'$or': [{MongoDBStorage._serialize_group_field_name(field): {'$gte': min_return}} for field in
                               return_fields]}

        return {
            '$match': {
                **min_returns,
                "count": {'$gte': min_count},
            }
        }

    @staticmethod
    def _generate_min_fields_match_stage_short(min_count: int, return_fields: List[str], min_return: float) -> object:
        min_returns = {'$or': [{MongoDBStorage._serialize_group_field_name(field): {'$lte': -min_return}} for field in
                               return_fields]}

        return {
            '$match': {
                **min_returns,
                "count": {'$gte': min_count},
            }
        }

    def save(self, candle: Candle):
        self._ensure_connection()

        self.candles_collection.replace_one(self._serialize_candle_key(candle), self._serialize_candle(candle),
                                            upsert=True)

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

    def get_symbol_candles(self, symbol: str, time_span: TimeSpan,
                           from_timestamp: datetime, to_timestamp: datetime, limit: int = 0) -> List[Candle]:
        self._ensure_connection()

        query = {
            'symbol': symbol,
            'timespan': time_span.value,
            'timestamp': {"$gte": from_timestamp, "$lte": to_timestamp}
        }

        return [self._deserialize_candle(candle) for candle in
                self.candles_collection.find(query).sort("timestamp").limit(limit)]

    def get_candles(self, time_span: TimeSpan,
                    from_timestamp: datetime, to_timestamp: datetime) -> List[Candle]:
        self._ensure_connection()

        query = {
            'timespan': time_span.value,
            'timestamp': {"$gte": from_timestamp, "$lte": to_timestamp}
        }

        return [self._deserialize_candle(candle) for candle in
                self.candles_collection.find(query).sort("timestamp")]

    def __drop_collections__(self):
        self._ensure_connection()
        self.db.drop_collection(CANDLES_COLLECTION)

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'host': self.host,
            'port': self.port,
            'database': self.database,
            'username': self.username,
            'password': self.password,
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        return cls(data.get('host'), data.get('port'), data.get('database'), data.get('username'), data.get('password'))
