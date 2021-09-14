from typing import Callable

from entities.candle import Candle
from pipeline.processor import Processor
from pipeline.shared_context import SharedContext


class ValidationProcessor(Processor):
    def __init__(self, callback: Callable[[SharedContext, Candle], None]) -> None:
        super().__init__(None)
        self.callback = callback

    def process(self, context: SharedContext, candle: Candle):
        self.callback(context, candle)
