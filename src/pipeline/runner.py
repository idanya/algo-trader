import logging
from typing import List, Union

from pipeline.pipeline import Pipeline
from pipeline.shared_context import SharedContext


class PipelineRunner:
    logger = logging.getLogger('PipelineRunner')

    def __init__(self, pipelines: Union[Pipeline, List[Pipeline]], context = SharedContext()) -> None:
        if pipelines is not list:
            pipelines = [pipelines]
     
        self.pipelines = pipelines
        self.context = context

    def run(self):
        self.logger.info('Starting pipeline runner...')
        for pipeline in self.pipelines:
            pipeline.run(self.context)