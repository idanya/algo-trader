from typing import Literal

from algotrader.entities.attachments.technicals import IndicatorValue
from algotrader.entities.generic_candle_attachment import GenericCandleAttachment


class AssetCorrelation(GenericCandleAttachment[IndicatorValue]):
    type: Literal["AssetCorrelation"] = "AssetCorrelation"
