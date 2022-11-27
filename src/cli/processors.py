from typing import List

import typer

from cli.helpers import _get_all_of_class, _describe_object
from pipeline.processor import Processor

app = typer.Typer()


@app.command()
def list():
    results = [p.__name__ for p in _get_processors()]
    print('\n'.join(results))


@app.command()
def describe(name: str):
    processor = _get_processor(name)
    _describe_object(processor)


def _get_processor(name: str) -> Processor:
    return next(filter(lambda p: p.__name__ == name, _get_processors()))


def _get_processors() -> List[Processor]:
    return [p for p in _get_all_of_class(Processor)]
