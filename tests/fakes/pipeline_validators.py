from typing import Callable

from entities.candle import Candle
from pipeline.processor import Processor
from pipeline.shared_context import SharedContext
from pipeline.terminator import Terminator


class ValidationProcessor(Processor):
    def __init__(self, callback: Callable[[SharedContext, Candle], None]) -> None:
        super().__init__(None)
        self.callback = callback

    def process(self, context: SharedContext, candle: Candle):
        self.callback(context, candle)


class TerminatorValidator(Terminator):
    def __init__(self, callback: Callable[[SharedContext], None]) -> None:
        self.callback = callback

    def terminate(self, context: SharedContext):
        self.callback(context)
