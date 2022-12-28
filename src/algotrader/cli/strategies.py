import typer

from cli.helpers import _describe_object, _get_all_of_class_names, _get_single_by_name
from entities.strategy import Strategy

app = typer.Typer(no_args_is_help=True)


@app.command()
def list():
    print('\n'.join(_get_all_of_class_names(Strategy)))


@app.command()
def describe(name: str):
    strategy = _get_single_by_name(Strategy, name)
    _describe_object(strategy)
