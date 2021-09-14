from __future__ import annotations

from abc import abstractmethod
from typing import Optional

from entities.candle import Candle
from pipeline.shared_context import SharedContext


class Processor:
    def __init__(self, next_processor: Optional[Processor]) -> None:
        self.next_processor = next_processor

    @abstractmethod
    def process(self, context: SharedContext, candle: Candle):
        pass
