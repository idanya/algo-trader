from abc import abstractmethod

from pipeline.shared_context import SharedContext


class Terminator:
    @abstractmethod
    def terminate(self, context: SharedContext):
        pass
