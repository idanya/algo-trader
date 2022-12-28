import json

import typer

from algotrader.pipeline.pipeline import Pipeline
from algotrader.pipeline.runner import PipelineRunner
from algotrader.serialization.store import DeserializationService

app = typer.Typer(no_args_is_help=True)


def load_pipeline_spec(file_path: str) -> Pipeline:
    with open(file_path, 'r') as input_file:
        return DeserializationService.deserialize(json.loads(input_file.read()))


@app.command()
def run(path: str):
    """
    Create and run a JSON serialized pipeline from file
    """
    pipeline = load_pipeline_spec(path)
    PipelineRunner(pipeline).run()
