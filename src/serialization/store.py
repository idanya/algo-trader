from __future__ import annotations

from typing import Dict, Optional
from typing import TYPE_CHECKING
import importlib

if TYPE_CHECKING:
    from entities.serializable import Deserializable

deserializers: Dict[str, Deserializable] = {

}


class DeserializationService:
    @staticmethod
    def register(obj: Deserializable):
        name = obj.__class__.__name__
        if name not in deserializers:
            deserializers[name] = obj

    @staticmethod
    def deserialize(data: Dict) -> Optional[Deserializable]:
        if data is None or data.get('__class__') is None:
            return None

        class_name = data.get('__class__')
        mod_name, cls_name = class_name.split(':')
        mod = importlib.import_module(mod_name)
        cls: Deserializable = getattr(mod, cls_name)
        return cls.deserialize(data)

        # cls = __import__(class_name, globals())
        # deserialize = getattr(cls, 'deserialize')
        # return deserialize(data)

        # if class_name and class_name in deserializers:
        #     return deserializers[class_name].deserialize(data)
