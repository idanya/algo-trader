from __future__ import annotations

from datetime import datetime
from typing import Callable, Dict, Optional

from algotrader.entities.candle_attachments import CandleAttachments
from algotrader.entities.serializable import Serializable, Deserializable
from algotrader.entities.timespan import TimeSpan
from algotrader.serialization.store import DeserializationService

timestamp_to_str: Callable[[datetime], str] = lambda d: d.strftime("%Y%m%d %H:%M:%S.%f")
str_to_timestamp: Callable[[str], datetime] = lambda d: datetime.strptime(d, "%Y%m%d %H:%M:%S.%f")


class Candle(Serializable, Deserializable):
    def __init__(self, symbol: str, time_span: TimeSpan, timestamp: datetime, open: float, close: float, high: float,
                 low: float, volume: float, attachments: Optional[CandleAttachments] = None):
        self.symbol = symbol
        self.timestamp = timestamp
        self.time_span = time_span

        self.open = open
        self.close = close
        self.high = high
        self.low = low
        self.volume = volume
        self.attachments = attachments or CandleAttachments()

    def add_attachement(self, key: str, data: Serializable):
        self.attachments.add_attachement(key, data)

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'symbol': self.symbol,
            'timestamp': timestamp_to_str(self.timestamp),
            'timespan': self.time_span.value,
            'open': self.open,
            'close': self.close,
            'high': self.high,
            'low': self.low,
            'volume': self.volume,
            'attachments': self.attachments.serialize()
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict) -> Candle:
        return cls(data['symbol'], TimeSpan(data['timespan']), str_to_timestamp(data['timestamp']), data['open'],
                   data['close'], data['high'], data['low'], data['volume'],
                   DeserializationService.deserialize(data.get('attachments')))
