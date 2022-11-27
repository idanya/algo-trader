from typing import List

import typer

from cli.helpers import _get_all_of_class, _describe_object
from entities.strategy import Strategy

app = typer.Typer()


@app.command()
def list():
    results = [p.__name__ for p in _get_strategies()]
    print('\n'.join(results))


@app.command()
def describe(name: str):
    strategy = _get_strategy(name)
    _describe_object(strategy)


def _get_strategy(name: str) -> Strategy:
    return next(filter(lambda p: p.__name__ == name, _get_strategies()))


def _get_strategies() -> List[Strategy]:
    return [p for p in _get_all_of_class(Strategy)]
