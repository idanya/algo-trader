from __future__ import annotations

from typing import Dict, Optional, ItemsView

from algotrader.entities.bucket import Bucket, CompoundBucketList
from algotrader.entities.serializable import Serializable, Deserializable
from algotrader.serialization.store import DeserializationService


class BucketsContainer(Serializable, Deserializable):
    def __init__(self) -> None:
        super().__init__()
        self.bins: Dict[str, CompoundBucketList] = {}

    def items(self) -> ItemsView[str, CompoundBucketList]:
        return self.bins.items()

    def add(self, indicator: str, value: CompoundBucketList):
        self.bins[indicator] = value

    def get(self, indicator: str) -> Optional[CompoundBucketList]:
        return self.bins[indicator] if indicator in self.bins else None

    def serialize(self) -> Dict:
        data = super().serialize()
        for key, value in self.bins.items():
            if isinstance(value[0], list):
                data[key] = []
                for arr in value:
                    data[key].append([x.serialize() for x in arr])
            elif isinstance(value[0], Bucket):
                data[key] = [x.serialize() for x in value]

        return data

    @classmethod
    def deserialize(cls, data: Dict) -> BucketsContainer:
        bins = BucketsContainer()
        for key, value in data.items():
            if key == '__class__':
                continue

            if isinstance(value[0], list):
                lists = []
                for lst in value:
                    lists.append([DeserializationService.deserialize(x) for x in lst])

                bins.add(key, lists)
            else:
                bins.add(key, [DeserializationService.deserialize(x) for x in value])

        return bins


BucketsContainer()
