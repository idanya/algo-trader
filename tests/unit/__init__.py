from datetime import datetime

from algotrader.entities.candle import Candle
from algotrader.entities.timespan import TimeSpan

TEST_SYMBOL = 'X'


def generate_candle_with_symbol(symbol: str, time_span: TimeSpan, timestamp: datetime) -> Candle:
    return Candle(symbol=symbol, time_span=time_span, timestamp=timestamp,
                  open=0.0, close=0.0, high=0.0, low=0.0, volume=0.0)


def generate_candle(time_span: TimeSpan, timestamp: datetime) -> Candle:
    return generate_candle_with_symbol(TEST_SYMBOL, time_span, timestamp)


def generate_candle_with_price(time_span: TimeSpan, timestamp: datetime, price: float) -> Candle:
    candle = generate_candle(time_span, timestamp)
    candle.open = candle.close = candle.high = candle.low = candle.volume = price
    return candle


def generate_candle_with_price_and_symbol(symbol: str, time_span: TimeSpan, timestamp: datetime,
                                          price: float) -> Candle:
    candle = generate_candle_with_symbol(symbol, time_span, timestamp)
    candle.open = candle.close = candle.high = candle.low = candle.volume = price
    return candle
