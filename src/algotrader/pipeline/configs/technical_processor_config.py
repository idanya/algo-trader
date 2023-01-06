from __future__ import annotations

from typing import List, Dict

from algotrader.entities.serializable import Deserializable, Serializable
from algotrader.pipeline.configs.indicator_config import IndicatorConfig


class TechnicalsProcessorConfig(Serializable, Deserializable):
    def __init__(self, technicals: List[IndicatorConfig]):
        self.technicals = technicals

    def serialize(self) -> Dict:
        return {
            "technicals": [t.serialize() for t in self.technicals]
        }

    @classmethod
    def deserialize(cls, data: Dict) -> TechnicalsProcessorConfig:
        return TechnicalsProcessorConfig(
            technicals=[IndicatorConfig.deserialize(t) for t in data["technicals"]]
        )
