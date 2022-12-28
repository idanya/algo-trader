from __future__ import annotations

from typing import Dict, TypeVar, Generic, Optional, ItemsView, Union

from algotrader.entities.serializable import Serializable, Deserializable

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
        data = {}
        for k, v in self._data.items():
            if k == '__class__':
                continue
            data.update({k: v})

        return data.items()

    @classmethod
    def deserialize(cls, data: Dict) -> GenericCandleAttachment:
        obj = GenericCandleAttachment()
        obj._data = data
        return obj

    def serialize(self) -> Dict:
        obj = super().serialize()
        for k, v in self._data.items():
            if v:
                if isinstance(v, list):
                    obj[k] = [self._serialized_value(x) for x in v]
                else:
                    obj[k] = self._serialized_value(v)

        return obj

    @staticmethod
    def _serialized_value(value: Union[any, Serializable]):
        return value.serialize() if isinstance(value, Serializable) else value

    def has(self, key: str):
        return key in self._data and self._data[key] is not None
