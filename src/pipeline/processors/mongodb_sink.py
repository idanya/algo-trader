from typing import Optional

from entities.candle import Candle
from pipeline.processor import Processor
from pipeline.shared_context import SharedContext
from storage.mongodb_storage import MongoDBStorage


class MongoDBSinkProcessor(Processor):

    def __init__(self, mongo_storage: MongoDBStorage, next_processor: Optional[Processor] = None) -> None:
        super().__init__(next_processor)
        self.mongo_storage = mongo_storage

    def process(self, context: SharedContext, candle: Candle):
        self.mongo_storage.save(candle)
        super().process(context, candle)

    def reprocess(self, context: SharedContext, candle: Candle):
        self.mongo_storage.save(candle)
        super().reprocess(context, candle)
