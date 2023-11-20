from __future__ import annotations

from typing import Dict, TypeVar, Generic, Optional, ItemsView

from pydantic import Field

from algotrader.entities.base_dto import BaseEntity

T = TypeVar("T")


class GenericCandleAttachment(Generic[T], BaseEntity):
    data: Dict[str, T] = Field(default_factory=dict)

    def __getitem__(self, key):
        return self.data[key]

    def set(self, key: str, value: T):
        self.data[key] = value

    def get(self, key: str) -> Optional[T]:
        return self.data[key]

    def items(self) -> ItemsView[str, T]:
        data = {}
        for k, v in self.data.items():
            if k == "__class__":
                continue
            data.update({k: v})

        return data.items()

    def has(self, key: str):
        return key in self.data and self.data[key] is not None
