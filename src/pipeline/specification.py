from typing import Optional, Dict

from entities.serializable import Serializable, Deserializable
from pipeline.processor import Processor
from pipeline.source import Source
from pipeline.terminator import Terminator
from serialization.store import DeserializationService


class PipelineSpecification(Serializable, Deserializable):
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
