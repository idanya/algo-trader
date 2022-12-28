from enum import Enum


class SignalDirection(Enum):
    Long = 1
    Short = 2


class StrategySignal:
    def __init__(self, symbol: str, direction: SignalDirection) -> None:
        self.symbol = symbol
        self.direction = direction
