from pipeline.processor import Processor
from pipeline.shared_context import SharedContext
from pipeline.source import Source


class PipelineRunner:
    def __init__(self, source: Source, processor: Processor) -> None:
        self.source = source
        self.processor = processor

    def run(self):
        context = SharedContext()
        for candle in self.source.read():
            self.processor.process(context, candle)
