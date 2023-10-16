from __future__ import annotations

from typing import Dict, Optional, Union

from algotrader.entities.attachments.nothing import NothingClass
from algotrader.entities.serializable import Serializable, Deserializable
from algotrader.entities.attachments.technicals_buckets_matcher import IndicatorsMatchedBuckets
from algotrader.entities.attachments.assets_correlation import AssetCorrelation
from algotrader.entities.attachments.technicals import Indicators
from algotrader.entities.attachments.technicals_normalizer import NormalizedIndicators
from algotrader.serialization.store import DeserializationService

CandleAttachment = Union[NothingClass, NormalizedIndicators, Indicators, AssetCorrelation, IndicatorsMatchedBuckets]


class CandleAttachments(Serializable, Deserializable):
    def __init__(self) -> None:
        super().__init__()
        self.data: Dict[str, Serializable] = {}

    @classmethod
    def deserialize(cls, data: Dict):
        obj = CandleAttachments()
        for k, v in data.items():
            if k != "__class__" and isinstance(v, dict) and "__class__" in v:
                obj.add_attachement(k, DeserializationService.deserialize(v))

        return obj

    def add_attachement(self, key: str, data: Serializable):
        self.data[key] = data

    def get_attachment(self, key: str) -> Optional[Serializable]:
        return self.data.get(key, None)

    def serialize(self) -> Dict:
        obj = super().serialize()

        for k, v in self.data.items():
            if v:
                obj[k] = v.serialize()

        return obj
