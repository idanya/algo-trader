from abc import abstractmethod
from typing import Dict

from serialization.store import DeserializationService


class Serializable:
    @abstractmethod
    def serialize(self) -> Dict:
        return {'__class__': self.__class__.__name__}


class Deserializable:
    def __init__(self) -> None:
        DeserializationService.register(self)

    @classmethod
    @abstractmethod
    def deserialize(cls, data: Dict):
        pass
