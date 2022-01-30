import logging
from typing import Optional

from pipeline.processor import Processor
from pipeline.shared_context import SharedContext
from pipeline.source import Source
from pipeline.terminator import Terminator


class PipelineRunner:
    logger = logging.getLogger('PipelineRunner')

    def __init__(self, source: Source, processor: Processor, terminator: Optional[Terminator] = None) -> None:
        self.source = source
        self.processor = processor
        self.terminator = terminator

    def run(self):
        self.logger.info('starting pipeline...')
        context = SharedContext()
        for candle in self.source.read():
            self.processor.process(context, candle)

        if self.terminator:
            self.terminator.terminate(context)
