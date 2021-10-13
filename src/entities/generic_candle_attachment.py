from __future__ import annotations

from typing import Dict, TypeVar, Generic, Optional, ItemsView

from entities.serializable import Serializable, Deserializable

T = TypeVar('T')


class GenericCandleAttachment(Generic[T], Serializable, Deserializable):
    def __init__(self) -> None:
        super().__init__()
        self._data: Dict[str, T] = {}

    def __getitem__(self, key):
        return self._data[key]

    def set(self, key: str, value: T):
        self._data[key] = value

    def get(self, key: str) -> Optional[T]:
        return self._data[key]

    def items(self) -> ItemsView[str, T]:
        return self._data.items()

    @classmethod
    def deserialize(cls, data: Dict) -> GenericCandleAttachment:
        obj = GenericCandleAttachment()
        obj._data = data
        return obj

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update(self._data)
        return obj

    def has(self, key: str):
        return key in self._data and self._data[key] is not None
