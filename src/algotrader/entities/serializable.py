from typing import Dict


class Serializable:
    def serialize(self) -> Dict:
        module = self.__class__.__module__
        name = self.__class__.__name__
        return {'__class__': f'{module}:{name}'}


class Deserializable:
    @classmethod
    def deserialize(cls, data: Dict):
        return cls()
