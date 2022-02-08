from __future__ import annotations

from abc import abstractmethod
from typing import Optional

from entities.candle import Candle
from entities.event import Event
from pipeline.shared_context import SharedContext


class Processor:
    def __init__(self, next_processor: Optional[Processor]) -> None:
        self.next_processor = next_processor

    @abstractmethod
    def process(self, context: SharedContext, candle: Candle):
        if self.next_processor:
            self.next_processor.process(context, candle)

    def reprocess(self, context: SharedContext, candle: Candle):
        if self.next_processor:
            self.next_processor.reprocess(context, candle)

    def event(self, context: SharedContext, event: Event):
        if self.next_processor:
            self.next_processor.event(context, event)
