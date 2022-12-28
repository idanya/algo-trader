from __future__ import annotations

import importlib
from typing import Dict, Optional, TypeVar, Generic
# from typing import TYPE_CHECKING

# if TYPE_CHECKING:
from algotrader.entities.serializable import Deserializable

T = TypeVar('T', bound=Deserializable)


class DeserializationService(Generic[T]):
    @staticmethod
    def deserialize(data: Dict) -> Optional[T]:
        if data is None or data.get('__class__') is None:
            return None

        class_name = data.get('__class__')
        mod_name, cls_name = class_name.split(':')
        mod = importlib.import_module(mod_name)
        cls: Deserializable = getattr(mod, cls_name)
        return cls.deserialize(data)
