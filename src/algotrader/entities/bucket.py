from __future__ import annotations

from typing import Dict, List, Union

from algotrader.entities.serializable import Serializable, Deserializable


class Bucket(Serializable, Deserializable):
    def __init__(self, ident: int, start: float = float('-inf'), end: float = float('inf')) -> None:
        super().__init__()
        self.ident = ident
        self.start = start
        self.end = end

    @classmethod
    def deserialize(cls, data: Dict) -> Bucket:
        return Bucket(data['ident'], data['start'], data['end'])

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'ident': self.ident,
            'start': self.start,
            'end': self.end
        })

        return obj


BucketList = List[Bucket]
CompoundBucketList = Union[List[BucketList], BucketList]

Bucket(0)
