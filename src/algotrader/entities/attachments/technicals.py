from __future__ import annotations

from typing import Literal, Union, List

from algotrader.entities.generic_candle_attachment import GenericCandleAttachment

IndicatorValue = Union[List[float], float]


class Indicators(GenericCandleAttachment[IndicatorValue]):
    type: Literal["Indicators"] = "Indicators"
