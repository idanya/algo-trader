from __future__ import annotations

from datetime import datetime
from typing import Callable, Dict

from entities.timespan import TimeSpan

timestamp_to_str: Callable[[datetime], str] = lambda d: d.strftime("%Y%m%d %H:%M:%S.%f")
str_to_timestamp: Callable[[str], datetime] = lambda d: datetime.strptime(d, "%Y%m%d %H:%M:%S.%f")


class Candle:
    def __init__(self, symbol: str, time_span: TimeSpan, timestamp: datetime, open: float, close: float, high: float,
                 low: float, volume: float):
        self.symbol = symbol
        self.timestamp = timestamp
        self.time_span = time_span

        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume

    def serialize(self) -> Dict:
        return {
            'symbol': self.symbol,
            'timestamp': timestamp_to_str(self.timestamp),
            'timespan': self.time_span.name,
            'open': self.open,
            'close': self.close,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
        }

    @staticmethod
    def deserialize(data: Dict) -> Candle:
        return Candle(data['symbol'], TimeSpan[data['timespan']], str_to_timestamp(data['timestamp']), data['open'],
                      data['close'], data['high'], data['low'], data['volume'])
