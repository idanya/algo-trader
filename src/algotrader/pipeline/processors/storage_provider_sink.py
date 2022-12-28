from typing import Optional, Dict

from algotrader.entities.candle import Candle
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.shared_context import SharedContext
from algotrader.serialization.store import DeserializationService
from algotrader.storage.storage_provider import StorageProvider


class StorageSinkProcessor(Processor):
    """
    Write all processed candles to a StorageProvider implementation
    """

    def __init__(self, storage_provider: StorageProvider, next_processor: Optional[Processor] = None) -> None:
        """
        @param storage_provider: StorageProvider implementation
        """
        super().__init__(next_processor)
        self.storage_provider = storage_provider

    def process(self, context: SharedContext, candle: Candle):
        self.storage_provider.save(candle)
        super().process(context, candle)

    def reprocess(self, context: SharedContext, candle: Candle):
        self.storage_provider.save(candle)
        super().reprocess(context, candle)

    def serialize(self) -> Dict:
        obj = super().serialize()
        obj.update({
            'storage_provider': self.storage_provider.serialize(),
        })
        return obj

    @classmethod
    def deserialize(cls, data: Dict):
        storage_provider = DeserializationService.deserialize(data['storage_provider'])
        return cls(storage_provider, cls._deserialize_next_processor(data))
