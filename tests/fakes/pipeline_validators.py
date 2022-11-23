from typing import Callable

from entities.candle import Candle
from entities.event import Event
from pipeline.processor import Processor
from pipeline.shared_context import SharedContext
from pipeline.terminator import Terminator


class ValidationProcessor(Processor):

    def __init__(self, process_callback: Callable[[SharedContext, Candle], None],
                 event_callback: Callable[[SharedContext, Event], None] = None) -> None:
        super().__init__(None)
        self.process_callback = process_callback
        self.event_callback = event_callback

    def process(self, context: SharedContext, candle: Candle):
        self.process_callback(context, candle)

    def event(self, context: SharedContext, event: Event):
        if self.event_callback:
            self.event_callback(context, event)


class TerminatorValidator(Terminator):
    def __init__(self, callback: Callable[[SharedContext], None]) -> None:
        self.callback = callback

    def terminate(self, context: SharedContext):
        self.callback(context)
