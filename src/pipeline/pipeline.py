from typing import Optional, Dict

from entities.serializable import Serializable, Deserializable
from pipeline.processor import Processor
from pipeline.shared_context import SharedContext
from pipeline.source import Source
from pipeline.terminator import Terminator
from serialization.store import DeserializationService


class Pipeline(Serializable, Deserializable):
    def __init__(self, source: Source, processor: Processor, terminator: Optional[Terminator] = None) -> None:
        self.source = source
        self.processor = processor
        self.terminator = terminator

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'source': self.source.serialize(),
            'processor': self.processor.serialize(),
            'terminator': self.terminator
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        return cls(DeserializationService.deserialize(data.get('source')),
                   DeserializationService.deserialize(data.get('processor')),
                   DeserializationService.deserialize(data.get('terminator')))

    def run(self, context: SharedContext) -> None:
        self.logger.info('Starting pipeline...')
        for candle in self.source.read():
            self.processor.process(context, candle)

        if self.terminator:
            self.terminator.terminate(context)

