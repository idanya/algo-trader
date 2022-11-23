from typing import Callable, Iterator

from entities.candle import Candle
from pipeline.shared_context import SharedContext
from pipeline.source import Source


class ContextInjectionFactorySource(Source):
    def __init__(self, context: SharedContext, factory: Callable[[SharedContext], Source]) -> None:
        super().__init__()
        self.context = context
        self.factory = factory

    def read(self) -> Iterator[Candle]:
        source = self.factory(self.context)
        for candle in source.read():
            yield candle
