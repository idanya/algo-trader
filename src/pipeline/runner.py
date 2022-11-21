import logging
from typing import List, Optional, Union

from pipeline.pipeline import Pipeline
from pipeline.shared_context import SharedContext


class PipelineRunner:
    logger = logging.getLogger('PipelineRunner')

    def __init__(self, pipelines: Union[Pipeline, List[Pipeline]], context: Optional[SharedContext] = None) -> None:
        if pipelines is not list:
            pipelines = [pipelines]
     
        self.pipelines : List[Pipeline] = pipelines
        if context is None:
            self.context = SharedContext()
        else:
            self.context = context

    def run(self):
        self.logger.info('Starting pipeline runner...')
        for pipeline in self.pipelines:
            pipeline.run(self.context)