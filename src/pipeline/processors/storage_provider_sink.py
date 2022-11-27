from typing import Optional

from entities.candle import Candle
from pipeline.processor import Processor
from pipeline.shared_context import SharedContext
from storage.storage_provider import StorageProvider


class StorageSinkProcessor(Processor):
    """
    Write all processed candles to a StorageProvider implementation
    """

    def __init__(self, storage_provider: StorageProvider, next_processor: Optional[Processor] = None) -> None:
        """
        @param storage_provider: StorageProvider implementation
        """
        super().__init__(next_processor)
        self.mongo_storage = storage_provider

    def process(self, context: SharedContext, candle: Candle):
        self.mongo_storage.save(candle)
        super().process(context, candle)

    def reprocess(self, context: SharedContext, candle: Candle):
        self.mongo_storage.save(candle)
        super().reprocess(context, candle)
