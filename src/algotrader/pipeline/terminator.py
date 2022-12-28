from abc import abstractmethod

from algotrader.entities.serializable import Deserializable, Serializable
from algotrader.pipeline.shared_context import SharedContext


class Terminator(Serializable, Deserializable):
    @abstractmethod
    def terminate(self, context: SharedContext):
        pass
