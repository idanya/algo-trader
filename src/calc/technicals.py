from __future__ import annotations

from typing import List

import numpy as np
import tulipy as ti

from entities.candle import Candle


class TechnicalCalculator:
    def __init__(self, candles: List[Candle]):
        self.candles = candles
        self.closes = np.array([c.close for c in candles])
        self.highs = np.array([c.high for c in candles])
        self.lows = np.array([c.low for c in candles])
        self.volumes = np.array([c.volume for c in candles])

    def sma(self, period: int) -> List[float]:
        if len(self.candles) < period:
            return []

        return ti.sma(self.closes, period=period)

    def adxr(self, period: int) -> List[float]:
        if len(self.closes) < period * 2 + 3:
            return []

        return ti.adxr(self.highs, self.lows, self.closes, period=period)

    def cci(self, period: int) -> List[float]:
        if len(self.closes) - 1 < period + 1:
            return []

        return ti.cci(self.highs, self.lows, self.closes, period=period)

    def obv(self) -> List[float]:
        return ti.obv(self.closes, self.volumes)

    def natr(self, period: int) -> List[float]:
        if len(self.closes) < period:
            return []

        return ti.natr(self.highs, self.lows, self.closes, period=period)

    def stoch(self, k_period: int, k_slow_period: int, d_period: int) -> List[List[float]]:
        if len(self.closes) - 1 < k_period + k_slow_period + 1:
            return [] * 2

        return ti.stoch(self.highs, self.lows, self.closes, k_period, k_slow_period, d_period)

    def fisher(self, period: int) -> List[float]:
        if len(self.highs) < period:
            return [] * 2

        return ti.fisher(self.highs, self.lows, period)

    def aroonosc(self, period: int) -> List[float]:
        if len(self.highs) < period:
            return []

        return ti.aroonosc(self.highs, self.lows, period)

    def ema(self, period: int) -> List[float]:
        if len(self.closes) < period:
            return []

        return ti.ema(self.closes, period=period)

    def var(self, period: int) -> List[float]:
        if len(self.closes) < period:
            return []

        return ti.var(self.closes, period=period)

    def stddev(self, values: List[float], period: int) -> List[float]:
        if len(values) < period:
            return []

        return ti.stddev(np.array(values), period=period)

    def meandev(self, values: List[float], period: int) -> List[float]:
        if len(values) < period:
            return []

        return ti.md(np.array(values), period=period)

    def macd(self, short_period: int, long_period: int, signal_period: int) -> List[float]:

        needed_history_count = max(short_period, long_period, signal_period)
        if len(self.closes) < needed_history_count:
            return [] * 3

        return ti.macd(self.closes, short_period=short_period, long_period=long_period,
                       signal_period=signal_period)

    def bbands(self, period: int) -> List[float]:
        if len(self.closes) < period:
            return [] * 3

        return ti.bbands(self.closes, period=period, stddev=2)

    def rsi(self, period: int) -> List[float]:
        if len(self.closes) < period + 1:
            return []

        return ti.rsi(np.array(self.closes), period=period)

    def mom(self, period: int) -> List[float]:
        if len(self.closes) < period + 1:
            return []

        return ti.mom(np.array(self.closes), period=period)

    def vosc(self, short_period: int, long_period: int) -> List[float]:
        if len(self.volumes) < long_period + 1:
            return []

        return ti.vosc(self.volumes, short_period, long_period)
