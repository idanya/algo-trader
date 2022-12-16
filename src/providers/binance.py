from datetime import datetime
from typing import List, Optional, Dict

from binance.client import Client

from entities.candle import Candle
from entities.serializable import Deserializable, Serializable
from entities.timespan import TimeSpan


class BinanceProvider(Serializable, Deserializable):

    def __init__(self, api_key: Optional[str] = '', api_secret: Optional[str] = ''):
        self.api_key = api_key
        self.api_secret = api_secret
        self.client = Client(api_key, api_secret)

    def get_symbol_history(self, symbol: str, interval: TimeSpan, start_time: datetime,
                           end_time: datetime = datetime.now()) -> List[Candle]:

        candles: List[Candle] = []
        lines = self.client.get_klines(symbol=symbol,
                                       interval=self._timespan_to_interval(interval),
                                       startTime=int(start_time.timestamp() * 1000),
                                       endTime=int(end_time.timestamp() * 1000))

        for line in lines:
            timestamp = self._timestamp_to_datetime(line[0])
            open = float(line[1])
            high = float(line[2])
            low = float(line[3])
            close = float(line[4])
            volume = float(line[5])

            candle = Candle(symbol, interval, timestamp, open, close, high, low, volume)
            candles.append(candle)

        return candles

    def serialize(self) -> Dict:
        return {
            'apiKey': self.api_key,
            'apiSecret': self.api_secret,
        }

    @classmethod
    def deserialize(cls, data: Dict):
        return cls(data.get('apiKey'), data.get('apiSecret'))

    @staticmethod
    def _timestamp_to_datetime(timestamp: int) -> datetime:
        return datetime.fromtimestamp(timestamp / 1000)

    @staticmethod
    def _timespan_to_interval(timespan: TimeSpan) -> str:
        if timespan == TimeSpan.Minute:
            return Client.KLINE_INTERVAL_1MINUTE
        elif timespan == TimeSpan.Hour:
            return Client.KLINE_INTERVAL_1HOUR
        elif timespan == TimeSpan.Day:
            return Client.KLINE_INTERVAL_1DAY
        else:
            raise ValueError('Unsupported timespan')
