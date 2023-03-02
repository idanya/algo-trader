from __future__ import annotations

from typing import List

import numpy as np
import tulipy as ti

from algotrader.calc.calculations import TechnicalCalculation
from algotrader.entities.candle import Candle


class TechnicalCalculator:

    def __init__(self, candles: List[Candle]):
        self._candles = candles
        self._closes = np.array([float(c.close) for c in candles])
        self._highs = np.array([float(c.high) for c in candles])
        self._lows = np.array([float(c.low) for c in candles])
        self._volumes = np.array([float(c.volume) for c in candles])

    def execute(self, calculation: TechnicalCalculation, params: List[any]) -> List[float]:
        return self.__getattribute__(calculation.value)(*params)

    def sma(self, period: int) -> List[float]:
        if len(self._candles) < period:
            return []

        return ti.sma(self._closes, period=period).tolist()

    def typical(self) -> List[float]:
        return ti.typprice(self._highs, self._lows, self._closes).tolist()

    def adxr(self, period: int) -> List[float]:
        if len(self._closes) < period * 2 + 3:
            return []

        return ti.adxr(self._highs, self._lows, self._closes, period=period).tolist()

    def cci(self, period: int) -> List[float]:
        if len(self._closes) - 1 < (period - 1) * 2:
            return []

        return ti.cci(self._highs, self._lows, self._closes, period=period).tolist()

    def obv(self) -> List[float]:
        return ti.obv(self._closes, self._volumes).tolist()

    def natr(self, period: int) -> List[float]:
        if len(self._closes) < period:
            return []

        return ti.natr(self._highs, self._lows, self._closes, period=period).tolist()

    def stoch(self, k_period: int, k_slow_period: int, d_period: int) -> List[List[float]]:
        if len(self._closes) - 1 < k_period + k_slow_period + 1:
            return [] * 2

        return ti.stoch(self._highs, self._lows, self._closes, k_period, k_slow_period, d_period)

    def fisher(self, period: int) -> List[float]:
        if len(self._highs) < period:
            return [] * 2

        return ti.fisher(self._highs, self._lows, period)

    def aroonosc(self, period: int) -> List[float]:
        if len(self._highs) <= period:
            return []

        return ti.aroonosc(self._highs, self._lows, period)

    def ema(self, period: int) -> List[float]:
        if len(self._closes) < period:
            return []

        return ti.ema(self._closes, period=period).tolist()

    def var(self, period: int) -> List[float]:
        if len(self._closes) < period:
            return []

        return ti.var(self._closes, period=period).tolist()

    def stddev(self, period: int) -> List[float]:
        if len(self._closes) < period:
            return []

        return ti.stddev(np.array(self._closes), period=period).tolist()

    def meandev(self, period: int) -> List[float]:
        if len(self._closes) < period:
            return []

        return ti.md(np.array(self._closes), period=period).tolist()

    def macd(self, short_period: int, long_period: int, signal_period: int) -> List[float]:

        needed_history_count = max(short_period, long_period, signal_period)
        if len(self._closes) < needed_history_count:
            return [] * 3

        return ti.macd(self._closes, short_period=short_period, long_period=long_period,
                       signal_period=signal_period)

    def bbands(self, period: int) -> List[float]:
        if len(self._closes) < period:
            return [] * 3

        return ti.bbands(self._closes, period=period, stddev=2)

    def rsi(self, period: int) -> List[float]:
        if len(self._closes) < period + 1:
            return []

        return ti.rsi(np.array(self._closes), period=period).tolist()

    def mom(self, period: int) -> List[float]:
        if len(self._closes) < period + 1:
            return []

        return ti.mom(np.array(self._closes), period=period).tolist()

    def vosc(self, short_period: int, long_period: int) -> List[float]:
        if len(self._volumes) < long_period + 1:
            return []

        return ti.vosc(self._volumes, short_period, long_period).tolist()
