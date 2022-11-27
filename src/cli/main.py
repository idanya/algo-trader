import json
import pathlib

import typer

from cli import processors, strategies
from pipeline.pipeline import Pipeline
from pipeline.runner import PipelineRunner
from serialization.store import DeserializationService

app = typer.Typer(no_args_is_help=True)
app.add_typer(processors.app, name='processor', short_help='Processors related commands')
app.add_typer(strategies.app, name='strategy', short_help='Strategies related commands')

EXAMPLE_TEMPLATES_DIR = pathlib.Path(__file__).parent.joinpath('examples/pipeline-templates').resolve()


def load_pipeline_spec(filename: str) -> Pipeline:
    with open(pathlib.Path(EXAMPLE_TEMPLATES_DIR).joinpath(filename), 'r') as input_file:
        return DeserializationService.deserialize(json.loads(input_file.read()))


@app.command()
def run_template(path: str):
    """
    Create and run a JSON serialized pipeline from file
    """
    pipeline = load_pipeline_spec(path)
    PipelineRunner(pipeline).run()


def initiate_cli():
    app()
