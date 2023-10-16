from __future__ import annotations

from typing import Literal

from algotrader.entities.generic_candle_attachment import GenericCandleAttachment


class Returns(GenericCandleAttachment[float]):
    type: Literal["Returns"] = "Returns"
