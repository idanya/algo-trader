from abc import abstractmethod

from entities.serializable import Deserializable, Serializable
from pipeline.shared_context import SharedContext


class Terminator(Serializable, Deserializable):
    @abstractmethod
    def terminate(self, context: SharedContext):
        pass
