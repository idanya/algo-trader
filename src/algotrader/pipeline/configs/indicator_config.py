from __future__ import annotations

from typing import List, Dict

from algotrader.calc.calculations import TechnicalCalculation
from algotrader.entities.serializable import Serializable, Deserializable


class IndicatorConfig(Serializable, Deserializable):
    def __init__(self, name: str, calculation: TechnicalCalculation, params: List[any]):
        self.name = name
        self.type = calculation
        self.params = params

    def serialize(self) -> Dict:
        return {
            "name": self.name,
            "type": self.type.value,
            "params": self.params
        }

    @classmethod
    def deserialize(cls, data: Dict) -> IndicatorConfig:
        return IndicatorConfig(data["name"], TechnicalCalculation(data["type"]), data["params"])
