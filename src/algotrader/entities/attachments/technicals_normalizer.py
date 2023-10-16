from __future__ import annotations

from typing import Literal

from algotrader.entities.attachments.technicals import IndicatorValue
from algotrader.entities.generic_candle_attachment import GenericCandleAttachment


class NormalizedIndicators(GenericCandleAttachment[IndicatorValue]):
    type: Literal["NormalizedIndicators"] = "NormalizedIndicators"
