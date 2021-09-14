from datetime import datetime

from entities.candle import Candle
from entities.timespan import TimeSpan

TEST_SYMBOL = 'X'


def generate_candle(time_span: TimeSpan, timestamp: datetime) -> Candle:
    return Candle(symbol=TEST_SYMBOL, time_span=time_span, timestamp=timestamp,
                  open=0.0, close=0.0, high=0.0, low=0.0, volume=0.0)


def generate_candle_with_price(time_span: TimeSpan, timestamp: datetime, price: float) -> Candle:
    candle = generate_candle(time_span, timestamp)
    candle.open = candle.close = candle.high = candle.low = candle.volume = price
    return candle
