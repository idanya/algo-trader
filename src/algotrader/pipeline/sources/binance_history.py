from datetime import datetime
from typing import Iterator, List, Dict

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.source import Source
from algotrader.providers.binance import BinanceProvider


class BinanceHistorySource(Source):
    def __init__(self, binance_provider: BinanceProvider, symbols: List[str], time_span: TimeSpan,
                 start_time: datetime, end_time: datetime = datetime.now()):
        self.binance_provider = binance_provider
        self.symbols = symbols
        self.time_span = time_span
        self.start_time = start_time
        self.end_time = end_time

    def read(self) -> Iterator[Candle]:
        for symbol in self.symbols:
            candles = self.binance_provider.get_symbol_history(symbol, self.time_span, self.start_time, self.end_time)
            for candle in candles:
                yield candle

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'binanceProvider': self.binance_provider.serialize(),
            'symbols': self.symbols,
            'timeSpan': self.time_span.value,
            'startTime': self.start_time.timestamp(),
            'endTime': self.end_time.timestamp(),
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        provider = BinanceProvider.deserialize(data.get('binanceProvider'))
        return cls(provider, data.get('symbols'), TimeSpan(data.get('timeSpan')),
                   datetime.fromtimestamp(data.get('startTime')),
                   datetime.fromtimestamp(data.get('endTime')))
