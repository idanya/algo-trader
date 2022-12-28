from __future__ import annotations

from abc import abstractmethod
from typing import Optional, Dict

from algotrader.entities.candle import Candle
from algotrader.entities.event import Event
from algotrader.entities.serializable import Deserializable, Serializable
from algotrader.pipeline.shared_context import SharedContext
from algotrader.serialization.store import DeserializationService


class Processor(Serializable, Deserializable):
    def __init__(self, next_processor: Optional[Processor] = None) -> None:
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

    @classmethod
    def deserialize(cls, data: Dict) -> Optional[Processor]:
        obj = cls(None)
        obj.next_processor = cls._deserialize_next_processor(data)
        return obj

    @classmethod
    def _deserialize_next_processor(cls, data: Dict) -> Optional[Processor]:
        if data.get('next_processor'):
            return DeserializationService.deserialize(data['next_processor'])
        return None

    def serialize(self) -> Dict:
        obj = super().serialize()

        if self.next_processor:
            obj.update({
                "next_processor": self.next_processor.serialize()
            })

        return obj
