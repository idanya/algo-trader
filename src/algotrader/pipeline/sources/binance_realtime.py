from queue import Queue
from typing import List, Dict, Iterator

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan
from algotrader.pipeline.source import Source
from algotrader.providers.binance import BinanceProvider


class BinanceRealtimeSource(Source):

    def __init__(self, binance_provider: BinanceProvider, symbols: List[str], time_span: TimeSpan):
        self.binance_provider = binance_provider
        self.symbols = symbols
        self.time_span = time_span
        self.queue = Queue()

        self._last_received_candle: Dict[str, Candle] = {}

    def read(self) -> Iterator[Candle]:
        for symbol in self.symbols:
            self.binance_provider.start_kline_socket(symbol, self.time_span, self._on_candle)

        while self.binance_provider.is_socket_alive():
            yield self.queue.get()

    def _on_candle(self, candle: Candle):
        if candle.symbol in self._last_received_candle and \
                candle.timestamp > self._last_received_candle[candle.symbol].timestamp:
            self.queue.put(self._last_received_candle[candle.symbol])

        self._last_received_candle[candle.symbol] = candle

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'binanceProvider': self.binance_provider.serialize(),
            'symbols': self.symbols,
            'timeSpan': self.time_span.value,
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        provider = BinanceProvider.deserialize(data.get('binanceProvider'))
        return cls(provider, data.get('symbols'), TimeSpan(data.get('timeSpan')))
