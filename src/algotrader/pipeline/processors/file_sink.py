import json
from typing import Optional

from algotrader.entities.candle import Candle
from algotrader.pipeline.processor import Processor
from algotrader.pipeline.shared_context import SharedContext


class FileSinkProcessor(Processor):
    """
    Write processed candles to file
    """

    def __init__(self, file_path: str, next_processor: Optional[Processor] = None) -> None:
        """
        @param file_path: file path to write to
        """
        super().__init__(next_processor)
        self.file_path = file_path

    def process(self, context: SharedContext, candle: Candle):
        with open(self.file_path, 'a') as output_file:
            line = self._generate_candle_output(context, candle)
            output_file.write(f'{line}\n')

        super().process(context, candle)

    def _generate_candle_output(self, context: SharedContext, candle: Candle) -> str:
        return json.dumps(candle.serialize())
