from __future__ import annotations
from typing import Dict, Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from entities.serializable import Deserializable

deserializers: Dict[str, Deserializable] = {

}


class DeserializationService:
    @staticmethod
    def register(obj: Deserializable):
        deserializers[obj.__class__.__name__] = obj

    @staticmethod
    def deserialize(data: Dict) -> Optional[Deserializable]:
        class_name = data.get('__class__')
        if class_name and class_name in deserializers:
            return deserializers[class_name].deserialize(data)
