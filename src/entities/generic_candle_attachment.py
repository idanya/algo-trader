from __future__ import annotations

from typing import Dict, TypeVar, Generic, Optional

from entities.serializable import Serializable, Deserializable

T = TypeVar('T')


class GenericCandleAttachment(Generic[T], Serializable, Deserializable):
    def __init__(self) -> None:
        super().__init__()
        self.data: Dict[str, T] = {}

    def __getitem__(self, key):
        return self.data[key]

    def set(self, key: str, value: T):
        self.data[key] = value

    def get(self, key: str) -> Optional[T]:
        return self.data[key]

    @classmethod
    def deserialize(cls, data: Dict) -> GenericCandleAttachment:
        obj = GenericCandleAttachment()
        obj.data = data
        return obj

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update(self.data)
        return obj

    def has(self, key: str):
        return key in self.data and self.data[key] is not None
