import logging
from typing import List, Optional, Union

from algotrader.pipeline.pipeline import Pipeline
from algotrader.pipeline.shared_context import SharedContext


class PipelineRunner:
    logger = logging.getLogger('PipelineRunner')

    def __init__(self, pipelines: Union[Pipeline, List[Pipeline]], context: Optional[SharedContext] = None) -> None:
        self.pipelines: List[Pipeline] = pipelines if isinstance(pipelines, list) else [pipelines]
        self.context = context or SharedContext()

    def run(self):
        self.logger.info('Starting pipeline runner...')
        for pipeline in self.pipelines:
            pipeline.run(self.context)
