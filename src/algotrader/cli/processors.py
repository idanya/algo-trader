import typer

from algotrader.cli.helpers import _describe_object, _get_all_of_class_names, _get_single_by_name
from algotrader.pipeline.processor import Processor

app = typer.Typer(no_args_is_help=True)


@app.command()
def list():
    print('\n'.join(_get_all_of_class_names(Processor)))


@app.command()
def describe(name: str):
    _describe_object(_get_single_by_name(Processor, name))
