from typing import Union, List, Literal

from algotrader.entities.bucket import Bucket
from algotrader.entities.generic_candle_attachment import GenericCandleAttachment


class IndicatorsMatchedBuckets(GenericCandleAttachment[Union[List[Bucket], Bucket]]):
    type: Literal["IndicatorsMatchedBuckets"] = "IndicatorsMatchedBuckets"
