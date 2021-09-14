from datetime import datetime

from entities.timespan import TimeSpan


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
