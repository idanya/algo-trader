import logging
from typing import Optional, Dict

from algotrader.entities.serializable import Serializable, Deserializable
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.shared_context import SharedContext
from algotrader.pipeline.source import Source
from algotrader.pipeline.terminator import Terminator
from algotrader.serialization.store import DeserializationService


class Pipeline(Serializable, Deserializable):
    logger = logging.getLogger('Pipeline')

    def __init__(self, source: Source, processor: Processor, terminator: Optional[Terminator] = None) -> None:
        self.source = source
        self.processor = processor
        self.terminator = terminator

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'source': self.source.serialize(),
            'processor': self.processor.serialize(),
            'terminator': self.terminator.serialize() if self.terminator else None,
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
            self.logger.debug('Processing candle: %s\r', candle.serialize())
            self.processor.process(context, candle)

        if self.terminator:
            self.logger.debug('initiating termination...')
            self.terminator.terminate(context)
